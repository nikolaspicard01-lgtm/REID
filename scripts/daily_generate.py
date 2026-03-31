"""
Daily auto-generation script.
Runs via GitHub Actions on a schedule.
Scrapes a Facebook profile for the top reel, transcribes it, and generates a script.
Saves the output to the /output folder.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.downloader import download_reel_audio
from utils.transcriber import transcribe_audio
from utils.script_generator import extract_concept, generate_script
from utils.profile_scraper import scrape_profile_reels


def main():
    profile_url = os.environ.get("FACEBOOK_PROFILE_URL")
    api_key = os.environ.get("CLAUDE_API_KEY")
    num_scripts = int(os.environ.get("NUM_SCRIPTS", "1"))

    if not profile_url:
        print("ERROR: FACEBOOK_PROFILE_URL not set")
        sys.exit(1)
    if not api_key:
        print("ERROR: CLAUDE_API_KEY not set")
        sys.exit(1)

    print(f"Scanning profile: {profile_url}")
    reels = scrape_profile_reels(profile_url, max_results=10)

    if not reels:
        print("No reels found. Exiting.")
        sys.exit(1)

    print(f"Found {len(reels)} reels. Processing top {num_scripts}...")

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
    )
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    for i, reel in enumerate(reels[:num_scripts]):
        print(f"\n--- Reel {i + 1}/{num_scripts}: {reel['title'][:50]} ---")

        try:
            # Download
            print("  Downloading audio...")
            audio_path = download_reel_audio(reel["url"])

            # Transcribe
            print("  Transcribing...")
            transcript = transcribe_audio(audio_path)

            # Cleanup audio
            try:
                os.remove(audio_path)
                os.rmdir(os.path.dirname(audio_path))
            except OSError:
                pass

            # Extract concept
            print("  Extracting concept...")
            concept = extract_concept(transcript, api_key)

            # Generate script
            print("  Generating script...")
            script = generate_script(concept, api_key)

            # Save
            filename = f"{today}_script_{i + 1}.md"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w") as f:
                f.write(f"# Generated: {today}\n")
                f.write(f"# Source: {reel['url']}\n")
                f.write(f"# Views: {reel['view_count']}\n\n")
                f.write("---\n\n")
                f.write("## CONCEPT\n\n")
                f.write(concept)
                f.write("\n\n---\n\n")
                f.write(script)

            print(f"  Saved to {filepath}")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print("\nDone!")


if __name__ == "__main__":
    main()
