"""Date utility functions."""

from datetime import datetime, timedelta, timezone


def get_last_week_range() -> tuple[datetime, datetime]:
    """
    Get the date range for the last complete week (Monday to Sunday).

    Returns:
        Tuple of (start_date, end_date) for the last complete week
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Find last Monday
    days_since_monday = (today.weekday() - 0) % 7
    if days_since_monday == 0:
        # If today is Monday, go back to last Monday
        days_since_monday = 7

    last_monday = today - timedelta(days=days_since_monday)
    last_sunday = last_monday + timedelta(days=6)
    last_sunday = last_sunday.replace(hour=23, minute=59, second=59)

    return last_monday, last_sunday


def parse_date_range(start_str: str | None, end_str: str | None) -> tuple[datetime, datetime]:
    """
    Parse date strings into datetime objects, or use default last week range.

    Args:
        start_str: Start date string in YYYY-MM-DD format (optional)
        end_str: End date string in YYYY-MM-DD format (optional)

    Returns:
        Tuple of (start_date, end_date)
    """
    if start_str and end_str:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
        end_date = datetime.strptime(end_str, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, microsecond=0, tzinfo=timezone.utc
        )
        return start_date, end_date

    return get_last_week_range()
