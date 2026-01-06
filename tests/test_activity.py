"""Tests for Activity data class."""

from datetime import datetime, timedelta, timezone

from weekly_summary.connectors.base import Activity


def test_activity_creation():
    """Test creating an Activity instance."""
    now = datetime.now(timezone.utc)
    activity = Activity(
        timestamp=now,
        title="Test Activity",
        description="Test description",
        source="test",
        activity_type="test_type",
        url="https://example.com",
        metadata={"key": "value"},
    )

    assert activity.timestamp == now
    assert activity.title == "Test Activity"
    assert activity.description == "Test description"
    assert activity.source == "test"
    assert activity.activity_type == "test_type"
    assert activity.url == "https://example.com"
    assert activity.metadata == {"key": "value"}


def test_activity_sorting():
    """Test that activities can be sorted by timestamp."""
    now = datetime.now(timezone.utc)
    activities = [
        Activity(
            timestamp=now + timedelta(hours=2),
            title="Later",
            description="",
            source="test",
            activity_type="test",
        ),
        Activity(
            timestamp=now,
            title="Earlier",
            description="",
            source="test",
            activity_type="test",
        ),
        Activity(
            timestamp=now + timedelta(hours=1),
            title="Middle",
            description="",
            source="test",
            activity_type="test",
        ),
    ]

    sorted_activities = sorted(activities)

    assert sorted_activities[0].title == "Earlier"
    assert sorted_activities[1].title == "Middle"
    assert sorted_activities[2].title == "Later"


def test_activity_optional_fields():
    """Test that optional fields can be None."""
    now = datetime.now(timezone.utc)
    activity = Activity(
        timestamp=now,
        title="Test",
        description="",
        source="test",
        activity_type="test",
    )

    assert activity.url is None
    assert activity.metadata is None
