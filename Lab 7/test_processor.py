
from hypothesis import given, strategies as st

from processor import (
    verify_isbn10_format,
    calculate_depreciation_factor,
    lookup_condition_multiplier
)


@given(st.text() | st.none())
def test_verify_isbn10_format_no_crash(s):
    try:
        verify_isbn10_format(s)
    except Exception as e:
        assert False, f"verify_isbn10_format crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_calculate_depreciation_factor_safe(s):
    try:
        calculate_depreciation_factor(s)
    except Exception as e:
        assert False, f"calculate_depreciation_factor crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_lookup_condition_multiplier_safe(s):
    try:
        lookup_condition_multiplier(s)
    except Exception as e:
        assert False, f"lookup_condition_multiplier crashed with input {s!r}: {e}"
