
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def test_invalid_batches_and_bonus():
    with pytest.raises(ValueError):
        process_book_buybacks("not-a-list", 5.0)
    with pytest.raises(ValueError):
        process_book_buybacks([], -1.0)


def test_unapproved_batch_is_skipped():
    result = process_book_buybacks([{"intake_approved": False}], 5.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


@pytest.mark.parametrize("book_format, expected", [
    ("textbook", 40.0),
    ("hardcover", 15.0),
    ("paperback", 8.0),
])
def test_each_supported_format(book_format, expected):
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": book_format,
        "books": [{"missing_pages": 0, "condition": "good", "counterfeit": False}],
    }], 5.0)
    assert result["total_payout"] == expected
    assert result["status"] == "COMPLETED"


def test_unknown_format_is_rejected():
    result = process_book_buybacks([{"intake_approved": True, "format": "audio", "books": []}], 5.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_missing_pages_are_rejected_but_other_book_is_paid():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [
            {"missing_pages": 2, "condition": "mint"},
            {"missing_pages": 0, "condition": "good"},
        ],
    }], 5.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_counterfeit_non_textbook_does_not_add_value():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "hardcover",
        "books": [{"counterfeit": True}, {"condition": "good"}],
    }], 5.0)
    assert result == {"total_payout": 15.0, "status": "COMPLETED"}


def test_counterfeit_textbook_cancels_batch_credit():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "textbook",
        "books": [{"condition": "mint"}, {"counterfeit": True}, {"condition": "good"}],
    }], 5.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


@pytest.mark.parametrize("condition, expected", [
    ("mint", 10.0),
    ("poor", 3.2),
    ("good", 8.0),
    ("worn", 8.0),
])
def test_book_conditions(condition, expected):
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"condition": condition}],
    }], 5.0)
    assert result["total_payout"] == expected


def test_store_credit_bonus():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "payout_in_credit": True,
        "books": [{"condition": "good"}],
    }], 5.0)
    assert result["total_payout"] == 13.0


def test_audit_rejected_after_more_than_four_rejections():
    result = process_book_buybacks([{
        "intake_approved": True,
        "format": "paperback",
        "books": [{"missing_pages": 1} for _ in range(5)],
    }], 5.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_scanner_no_data_and_calibrated():
    assert inspect_scanner_calibration([]) == "NO_DATA"
    assert inspect_scanner_calibration([[5, 4, 5], [0]]) == "CALIBRATED"


def test_scanner_recalibrates_after_two_consecutive_high_readings():
    assert inspect_scanner_calibration([[6, 7]]) == "RECALIBRATE"


def test_scanner_resets_streak_after_acceptable_reading():
    assert inspect_scanner_calibration([[6, 5, 7, 8]]) == "RECALIBRATE"
