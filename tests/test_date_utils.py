"""Tests for date utility functions."""

from datetime import timezone


from weekly_summary.utils.date_utils import get_last_week_range, parse_date_range


def test_get_last_week_range():
    """Test that get_last_week_range returns a Monday to Sunday range."""
    start, end = get_last_week_range()

    # Start should be a Monday at midnight
    assert start.weekday() == 0  # Monday
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0

    # End should be a Sunday at 23:59:59
    assert end.weekday() == 6  # Sunday
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59

    # Range should be 7 days
    assert (end.date() - start.date()).days == 6


def test_parse_date_range_with_dates():
    """Test parsing explicit date strings."""
    start, end = parse_date_range("2024-01-01", "2024-01-07")

    assert start.year == 2024
    assert start.month == 1
    assert start.day == 1
    assert start.hour == 0
    assert start.minute == 0

    assert end.year == 2024
    assert end.month == 1
    assert end.day == 7
    assert end.hour == 23
    assert end.minute == 59


def test_parse_date_range_without_dates():
    """Test that parse_date_range defaults to last week when no dates provided."""
    start, end = parse_date_range(None, None)

    # Should return same as get_last_week_range
    expected_start, expected_end = get_last_week_range()
    assert start == expected_start
    assert end == expected_end


def test_parse_date_range_timezone():
    """Test that dates are returned in UTC timezone."""
    start, end = parse_date_range("2024-01-01", "2024-01-07")

    assert start.tzinfo == timezone.utc
    assert end.tzinfo == timezone.utc
