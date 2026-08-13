import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render.resume_renderer import render_resume
from render.cover_renderer import render_cover_letter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILE_DIR = os.path.join(DATA_DIR, "profiles")
COVER_DIR = os.path.join(BASE_DIR, "cover_letters")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _slug(value):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")


def _list_files(directory, suffix=""):
    if not os.path.isdir(directory):
        return []
    names = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json"):
            names.append(filename[: -len(".json")])
    return names


def main():
    parser = argparse.ArgumentParser(
        description="Generate ATS-friendly resumes and cover letters as PDFs."
    )
    parser.add_argument(
        "--profile",
        action="append",
        help="Profile name from data/profiles. Repeatable. Use '--list-profiles' to see options.",
    )
    parser.add_argument(
        "--cover",
        action="append",
        help="Cover letter name from cover_letters. Repeatable. Use '--list-covers' to see options.",
    )
    parser.add_argument("--list-profiles", action="store_true", help="List available profiles.")
    parser.add_argument("--list-covers", action="store_true", help="List available cover letters.")
    args = parser.parse_args()

    if args.list_profiles:
        for name in _list_files(PROFILE_DIR):
            print(name)
        return

    if args.list_covers:
        for name in _list_files(COVER_DIR):
            print(name)
        return

    if not args.profile and not args.cover:
        parser.error("Provide at least one of --profile or --cover.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = _load(os.path.join(DATA_DIR, "resume.json"))

    generated = []

    for profile_name in args.profile or []:
        profile_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
        if not os.path.exists(profile_path):
            available = ", ".join(_list_files(PROFILE_DIR)) or "none"
            parser.error(f"Profile '{profile_name}' not found. Available: {available}")
        profile = _load(profile_path)
        filename = profile.get("filename") or f"Resume_{_slug(profile_name)}"
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.pdf")
        render_resume(data, profile, output_path)
        generated.append(output_path)

    for cover_name in args.cover or []:
        cover_path = os.path.join(COVER_DIR, f"{cover_name}.json")
        if not os.path.exists(cover_path):
            available = ", ".join(_list_files(COVER_DIR)) or "none"
            parser.error(f"Cover letter '{cover_name}' not found. Available: {available}")
        letter = _load(cover_path)
        company = _slug(letter.get("company", "Letter"))
        output_path = os.path.join(OUTPUT_DIR, f"CoverLetter_{company}.pdf")
        render_cover_letter(data, letter, output_path)
        generated.append(output_path)

    for path in generated:
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
