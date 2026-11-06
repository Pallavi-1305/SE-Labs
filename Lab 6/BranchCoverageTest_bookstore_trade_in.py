
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def test_validation_both_invalid_conditions():
    with pytest.raises(ValueError):
        process_book_buybacks(None, 1.0)
    with pytest.raises(ValueError):
        process_book_buybacks([], -0.1)


def test_batch_approval_true_and_false():
    result = process_book_buybacks([
        {"intake_approved": False},
        {"intake_approved": True, "format": "paperback", "books": []},
    ], 0)
    assert result["status"] == "ZERO_CREDIT"


@pytest.mark.parametrize("book_format, expected", [
    ("textbook", 40.0),
    ("hardcover", 15.0),
    ("paperback", 8.0),
    ("unknown", 0.0)
])
def test_format_decisions(book_format, expected):
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": book_format,
        "books": [{"missing_pages": 0, "condition": "good"}],
    }], 0)
    assert result["total_payout"] == expected


def test_missing_pages_true_and_false():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1}, {"missing_pages": 0}],
    }], 0)
    assert result["total_payout"] == 8.0


def test_counterfeit_textbook_and_non_textbook_paths():
    textbook = process_book_buybacks([{
        "intake_approved": True,
        "format": "textbook",
        "books": [{"counterfeit": True}, {"condition": "mint"}],
    }], 0)

    non_textbook = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"counterfeit": True}, {"condition": "poor"}],
    }], 0)

    assert textbook["status"] == "ZERO_CREDIT"
    assert non_textbook["total_payout"] == 3.2


@pytest.mark.parametrize("condition, expected", [
    ("mint", 10.0),
    ("poor", 3.2),
    ("good", 8.0)
])
def test_condition_branches(condition, expected):
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"condition": condition}],
    }], 0)
    assert result["total_payout"] == expected


def test_credit_bonus_true_and_false():
    credit = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": True,
        "books": [{"condition": "good"}],
    }], 2)

    cash = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": False,
        "books": [{"condition": "good"}],
    }], 2)

    assert credit["total_payout"] == 10.0
    assert cash["total_payout"] == 8.0


def test_audit_threshold_both_sides_and_zero_credit():
    below = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(4)],
    }], 0)

    above = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(5)],
    }], 0)

    zero = process_book_buybacks([], 0)

    assert below["status"] == "ZERO_CREDIT"
    assert above["status"] == "AUDIT_REJECTED"
    assert zero["status"] == "ZERO_CREDIT"


def test_scanner_empty_matrix():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_error_threshold_and_streak_branches():
    assert inspect_scanner_calibration([[5]]) == "CALIBRATED"
    assert inspect_scanner_calibration([[6]]) == "CALIBRATED"
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"
    assert inspect_scanner_calibration([[6, 5, 7, 8]]) == "RECALIBRATE"


def test_scanner_continues_to_next_device():
    assert inspect_scanner_calibration([[], [1, 2, 3]]) == "CALIBRATED"
