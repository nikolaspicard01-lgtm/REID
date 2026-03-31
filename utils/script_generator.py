import anthropic

CONCEPT_EXTRACTION_PROMPT = """Analyze this transcript from a Facebook reel and extract:

1. **Core Concept**: What is the central idea/hook of this story?
2. **Conflict Type**: What kind of conflict drives it? (betrayal, power imbalance, hidden identity, etc.)
3. **Emotional Arc**: What emotions does it take the viewer through?
4. **Target Hook**: What makes this concept compelling for a female audience aged 35-65?
5. **Key Themes**: List 3-5 themes present

Be concise. This will be used to generate a NEW original script based on the same concept.

TRANSCRIPT:
{transcript}"""

SCRIPT_GENERATION_PROMPT = """You are writing high-retention, emotionally driven vertical drama scripts designed for a female audience aged 35-65.

Based on the following concept extracted from a viral reel, write a COMPLETELY NEW and ORIGINAL script that uses the same core concept but with different characters, settings, and plot.

CONCEPT:
{concept}

RULES:

These are 7-9 minute narrative stories built for mobile viewing, but every single piece must also be engineered to extract multiple viral 30-60 second clips.

This is retention-first storytelling. If the story is ever "calm," "slow," or "comfortable," it is wrong.

CORE PRINCIPLE: Every minute must earn its place.

Each minute must include at least one of:
- A hook (new tension introduced)
- A twist (new information that reframes what we thought)
- A gap (a question left unanswered)
- A red herring (misdirection that creates curiosity)
- Emotional escalation (stakes getting higher)

OPENING (FIRST 3-5 SECONDS):
Start in the middle of tension. No setup. No exposition.
Examples: An accusation mid-sentence, a betrayal already happening, a shocking line that raises immediate questions.
The viewer must feel: "Wait... what is going on here?"

STRUCTURE (7-9 MINUTES):

Minute 0-1: Immediate conflict. No context. Drop us into chaos.
Minute 1-3: Layer information while increasing confusion or suspicion. Introduce characters through conflict, not explanation.
Minute 3-5: First major twist. What the viewer thought was happening is incomplete or wrong.
Minute 5-7: Escalation. Raise stakes emotionally. Add at least one red herring.
Minute 7-9: Payoff and reversal. Truth revealed publicly. Justice is visible and public.

End with: "They got exactly what they deserved."

CHARACTER DYNAMICS:
- Focus on relationships that create natural tension (mother-in-law vs partner, best friend betrayal, hidden identity, power imbalance)
- Protagonist must be underestimated
- Antagonist must feel real, not evil for no reason

EMOTIONAL ENGINE:
Build: Frustration -> curiosity -> outrage -> satisfaction
Justice must be visible and preferably public. Public vindication is powerful.

DIALOGUE STYLE:
- Short and sharp lines
- Use interruption, tension, and subtext
- Characters should not say everything — leave gaps

VIRAL CLIP ENGINEERING:
Mark 3-5 moments with [CLIP START] and [CLIP END] tags. These moments must:
- Start with tension immediately
- Contain a mini-arc (setup -> twist -> reaction)
- End with a question or reveal

RETENTION RULES:
- No filler scenes
- No repetitive dialogue
- No "safe" middle sections
- Every scene must reveal, escalate, or mislead

FORMAT YOUR OUTPUT IN PROPER SCREENPLAY FORMAT:

## TITLE
[Script title]

## LOGLINE
[One-sentence hook]

## SCRIPT

Use standard screenplay formatting:
- Scene headings: INT. or EXT. followed by LOCATION - TIME (all caps)
- Character names: centered, ALL CAPS before their dialogue
- Dialogue: indented under character name
- Action/description lines: full width, present tense
- Parentheticals: (whispered), (beat), (into phone) etc. under character name before dialogue
- Mark viral clip moments with [CLIP START] and [CLIP END] on their own lines

Example format:

INT. RESTAURANT - NIGHT

A crowded upscale restaurant. ELENA (42) sits across from her husband MARK (45), who keeps glancing at his phone.

[CLIP START]

ELENA
(calm, dangerous)
Who is she?

MARK
What are you talking about?

ELENA
The woman you just texted "I love you" to. While sitting across from your wife.

[CLIP END]

## CLIP BREAKDOWN
[List each clip-able moment with a one-line description]

Tone: grounded, emotional, slightly heightened reality.
Style: fast-paced, tension-driven, addictive.
Goal: make it impossible to scroll away."""


def extract_concept(transcript: str, api_key: str) -> str:
    """Extract the core concept from a transcript using Claude."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": CONCEPT_EXTRACTION_PROMPT.format(transcript=transcript),
            }
        ],
    )

    return message.content[0].text


def generate_script(concept: str, api_key: str) -> str:
    """Generate a new script based on the extracted concept using Claude."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": SCRIPT_GENERATION_PROMPT.format(concept=concept),
            }
        ],
    )

    return message.content[0].text


REVISION_PROMPT = """You are revising a screenplay script based on user feedback.

Here is the current script:

{script}

The user wants the following changes:

{feedback}

Rewrite the FULL script with these changes applied. Keep everything that works, only change what the user asked for. Maintain proper screenplay format (INT./EXT. headings, character names in caps, dialogue indented, [CLIP START]/[CLIP END] markers).

Output the complete revised script in the same format as the original (## TITLE, ## LOGLINE, ## SCRIPT, ## CLIP BREAKDOWN)."""


def revise_script(script: str, feedback: str, api_key: str) -> str:
    """Revise an existing script based on user feedback."""
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": REVISION_PROMPT.format(script=script, feedback=feedback),
            }
        ],
    )

    return message.content[0].text
