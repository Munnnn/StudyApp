"""Tests for CSV import parsing."""
import pytest
from app.services.csv_import import parse_csv


BASIC_CSV = """front,back,system_tag,topic_tag,difficulty
What causes hypercalcemia with low PTH?,Malignancy (PTHrP),endocrine,calcium,3
What is the mechanism of ACE inhibitors?,Block conversion of Ang I to Ang II,cardio,RAAS,2
"""

TSV_NO_TAGS = "front\tback\nWhat is troponin?\tMarker of myocardial injury\n"

EXTRA_COLS = "front,back,notes,difficulty\nFront text,Back text,ignore me,4\n"

ALT_SYSTEM_COL = "front,back,system,topic\nFront,Back,cardio,RAAS\n"


def test_basic_csv_parsed():
    cards = parse_csv(BASIC_CSV)
    assert len(cards) == 2
    assert cards[0].front == "What causes hypercalcemia with low PTH?"
    assert cards[0].back == "Malignancy (PTHrP)"
    assert cards[0].system_tag == "endocrine"
    assert cards[0].difficulty == 3


def test_tsv_accepted():
    cards = parse_csv(TSV_NO_TAGS)
    assert len(cards) == 1
    assert cards[0].front == "What is troponin?"
    assert cards[0].system_tag is None


def test_extra_columns_ignored():
    cards = parse_csv(EXTRA_COLS)
    assert len(cards) == 1
    assert cards[0].difficulty == 4


def test_alt_system_col_name():
    cards = parse_csv(ALT_SYSTEM_COL)
    assert cards[0].system_tag == "cardio"
    assert cards[0].topic_tag == "RAAS"


def test_empty_file_raises():
    with pytest.raises(ValueError, match="Empty file"):
        parse_csv("")


def test_missing_required_col():
    with pytest.raises(ValueError, match="Missing required columns"):
        parse_csv("front,notes\nSome front,some note\n")


def test_blank_rows_skipped():
    csv = "front,back\nGood front,Good back\n,,\n"
    cards = parse_csv(csv)
    assert len(cards) == 1


def test_difficulty_out_of_range_clamped():
    csv = "front,back,difficulty\nFront,Back,99\n"
    cards = parse_csv(csv)
    assert cards[0].difficulty == 5


def test_difficulty_invalid_string_defaults():
    csv = "front,back,difficulty\nFront,Back,notanumber\n"
    cards = parse_csv(csv)
    assert cards[0].difficulty == 2
