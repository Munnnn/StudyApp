"""Parse a CSV (or TSV) deck file into a list of CardCreate objects."""
import csv
import io
from typing import Optional

from app.schemas.card import CardCreate

REQUIRED_COLS = {"front", "back"}
OPTIONAL_COLS = {"system", "system_tag", "topic", "topic_tag", "difficulty"}


def parse_csv(text: str) -> list[CardCreate]:
    """
    Accepts comma or tab-delimited files.
    Supported headers (case-insensitive):
        front, back, system / system_tag, topic / topic_tag, difficulty
    Extra columns are silently ignored.
    """
    text = text.strip()
    if not text:
        raise ValueError("Empty file")

    # Sniff delimiter
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
    except csv.Error:
        dialect = csv.excel  # default to comma

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("No header row found")

    # Normalize headers
    headers = {h.strip().lower(): h for h in reader.fieldnames if h}
    missing = REQUIRED_COLS - set(headers.keys())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    def col(row: dict, *names: str) -> Optional[str]:
        for name in names:
            orig = headers.get(name)
            if orig and row.get(orig, "").strip():
                return row[orig].strip()
        return None

    cards: list[CardCreate] = []
    for i, row in enumerate(reader, start=2):
        front = col(row, "front")
        back = col(row, "back")
        if not front or not back:
            continue  # skip blank rows
        diff_raw = col(row, "difficulty")
        try:
            difficulty = max(1, min(5, int(diff_raw))) if diff_raw else 2
        except ValueError:
            difficulty = 2

        cards.append(
            CardCreate(
                front=front,
                back=back,
                system_tag=col(row, "system_tag", "system"),
                topic_tag=col(row, "topic_tag", "topic"),
                difficulty=difficulty,
            )
        )

    if not cards:
        raise ValueError("No valid rows found in CSV")
    return cards
