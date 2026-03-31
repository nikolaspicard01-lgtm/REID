import re
import tempfile
from fpdf import FPDF


class ScreenplayPDF(FPDF):
    """PDF formatted like a proper screenplay."""

    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(25, 25, 25)

    def title_page(self, title, logline=""):
        self.ln(80)
        self.set_font("Courier", "B", 24)
        self.cell(0, 15, title.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
        if logline:
            self.ln(10)
            self.set_font("Courier", "", 12)
            self.multi_cell(0, 6, logline, align="C")
        self.add_page()

    def scene_heading(self, text):
        self.ln(4)
        self.set_font("Courier", "B", 12)
        self.cell(0, 6, text.upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def action_line(self, text):
        self.set_font("Courier", "", 12)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def character_name(self, name):
        self.ln(2)
        self.set_font("Courier", "B", 12)
        # Character names are centered (indented ~3.7in from left in standard screenplay)
        self.cell(0, 6, name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")

    def parenthetical(self, text):
        self.set_font("Courier", "I", 12)
        x_offset = 55
        self.set_x(x_offset)
        self.cell(0, 6, f"({text})", new_x="LMARGIN", new_y="NEXT")

    def dialogue(self, text):
        self.set_font("Courier", "", 12)
        left_margin = 40
        right_margin = 40
        self.set_left_margin(left_margin)
        self.set_right_margin(right_margin)
        self.set_x(left_margin)
        self.multi_cell(0, 6, text)
        self.set_left_margin(25)
        self.set_right_margin(25)
        self.ln(1)

    def clip_marker(self, text):
        self.set_font("Courier", "B", 10)
        self.set_text_color(180, 40, 40)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)


def parse_script_to_pdf(script_text: str) -> bytes:
    """Parse a screenplay-formatted script and generate a PDF."""
    pdf = ScreenplayPDF()

    # Extract title and logline
    title = "Untitled Script"
    logline = ""

    title_match = re.search(r"(?:TITLE|Title)[:\s]*\n*(.+?)(?:\n|$)", script_text)
    if title_match:
        title = title_match.group(1).strip().strip("#").strip()

    logline_match = re.search(
        r"(?:LOGLINE|Logline)[:\s]*\n*(.+?)(?:\n\n|\n#|$)", script_text, re.DOTALL
    )
    if logline_match:
        logline = logline_match.group(1).strip()

    pdf.title_page(title, logline)

    # Find the script section
    script_section = script_text
    script_match = re.search(
        r"##\s*SCRIPT\s*\n(.*?)(?=##\s*CLIP|$)", script_text, re.DOTALL
    )
    if script_match:
        script_section = script_match.group(1)

    lines = script_section.strip().split("\n")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Clip markers
        if "[CLIP START]" in stripped or "[CLIP END]" in stripped:
            pdf.clip_marker(stripped)
            continue

        # Scene headings: INT. / EXT. or lines in all caps starting with these
        if re.match(r"^(INT\.|EXT\.|INT/EXT\.)", stripped, re.IGNORECASE):
            pdf.scene_heading(stripped)
            continue

        # Character names: all caps line, possibly with (V.O.) or (O.S.)
        if re.match(r"^[A-Z][A-Z\s\-\.]+(\s*\(.*?\))?\s*$", stripped) and len(stripped) < 40:
            pdf.character_name(stripped)
            continue

        # Parentheticals: lines in parentheses
        if re.match(r"^\(.*\)$", stripped):
            pdf.parenthetical(stripped.strip("()"))
            continue

        # Stage directions in brackets
        if re.match(r"^\[.*\]$", stripped):
            pdf.action_line(stripped.strip("[]"))
            continue

        # If previous line was a character name, this is dialogue
        # Default: treat as action/description
        pdf.action_line(stripped)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    tmp.seek(0)
    with open(tmp.name, "rb") as f:
        return f.read()
