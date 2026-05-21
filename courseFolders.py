#!/usr/bin/env python3
import argparse
import re
import unicodedata
from pathlib import Path
import pandas as pd


# ========= FORMAT SETTINGS =========
LOWERCASE = True          # True → make everything lowercase
REMOVE_SPACES = False # True → remove spaces entirely
SPACE_REPLACEMENT = "_"   # Used if REMOVE_SPACES = False
REMOVE_SWEDISH_CHARS = False
INCLUDE_TERM = False       # Create subfolders per term
# ===================================


def normalize_text(text: str) -> str:
    """Basic cleanup of text."""
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def remove_swedish(text: str) -> str:
    """Convert å ä ö etc to ascii equivalents."""
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def format_name(text: str) -> str:
    text = normalize_text(text)

    if REMOVE_SWEDISH_CHARS:
        text = remove_swedish(text)

    if LOWERCASE:
        text = text.lower()

    if REMOVE_SPACES:
        text = text.replace(" ", "")
    else:
        text = text.replace(" ", SPACE_REPLACEMENT)

    # Remove illegal/path-problem characters
    text = re.sub(r'[\/\\:*?"<>|]', "", text)

    return text


def cell(v) -> str:
    return "" if pd.isna(v) else str(v).strip()


def main():
    ap = argparse.ArgumentParser(description="Create formatted course folders.")
    ap.add_argument("excel_file", help="Path to .xlsx")
    ap.add_argument("-o", "--output", default=".", help="Output directory")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    excel_path = Path(args.excel_file).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(excel_path, sheet_name=0)

    required = ["Kurskod", "Kurs", "Termin"]
    for col in required:
        if col not in df.columns:
            raise SystemExit(f"Missing column: {col}")

    created = 0

    for _, row in df.iterrows():
        code = cell(row["Kurskod"])
        title = cell(row["Kurs"])
        term = cell(row["Termin"])

        if not code or not title:
            continue

        folder_name = format_name(f"{code}-{title}")

        if INCLUDE_TERM:
            term_folder = format_name(term or "okandtermin")
            final_path = out_dir / term_folder / folder_name
        else:
            final_path = out_dir / folder_name

        if args.dry_run:
            print(final_path)
        else:
            final_path.mkdir(parents=True, exist_ok=True)

        created += 1

    print(f"Created/ensured {created} folders.")


if __name__ == "__main__":
    main()
