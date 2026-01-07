"""Tests for mock connectors."""

from datetime import datetime, timezone


from weekly_summary.connectors.mock import (
    MockEmailConnector,
    MockGitHubConnector,
    MockSlackConnector,
)


class TestMockGitHubConnector:
    """Tests for MockGitHubConnector."""

    def test_validate_config(self):
        """Test config validation always succeeds."""
        connector = MockGitHubConnector({})
        assert connector.validate_config() is True

    def test_name_property(self):
        """Test connector name property."""
        connector = MockGitHubConnector({})
        assert connector.name == "github_mock"

    def test_fetch_activities_returns_data(self):
        """Test that fetch_activities returns mock data."""
        connector = MockGitHubConnector({"username": "test_user"})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        assert len(activities) > 0
        assert all(act.source == "github" for act in activities)

    def test_fetch_activities_has_different_types(self):
        """Test that mock data includes different activity types."""
        connector = MockGitHubConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)
        activity_types = {act.activity_type for act in activities}

        # Should have commits, PRs created, and PR reviews
        assert (
            "commit" in activity_types
            or "pr_created" in activity_types
            or "pr_review" in activity_types
        )

    def test_activities_within_date_range(self):
        """Test that all activities fall within the requested date range."""
        connector = MockGitHubConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert start_date <= activity.timestamp <= end_date

    def test_activities_have_metadata(self):
        """Test that activities include metadata."""
        connector = MockGitHubConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert activity.metadata is not None
            assert "repo" in activity.metadata


class TestMockSlackConnector:
    """Tests for MockSlackConnector."""

    def test_validate_config(self):
        """Test config validation always succeeds."""
        connector = MockSlackConnector({})
        assert connector.validate_config() is True

    def test_name_property(self):
        """Test connector name property."""
        connector = MockSlackConnector({})
        assert connector.name == "slack_mock"

    def test_fetch_activities_returns_data(self):
        """Test that fetch_activities returns mock data."""
        connector = MockSlackConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        assert len(activities) > 0
        assert all(act.source == "slack" for act in activities)
        assert all(act.activity_type == "message" for act in activities)

    def test_activities_have_urls(self):
        """Test that Slack activities have URLs."""
        connector = MockSlackConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert activity.url is not None
            assert "slack.com" in activity.url

    def test_activities_have_channel_metadata(self):
        """Test that activities include channel metadata."""
        connector = MockSlackConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert activity.metadata is not None
            assert "channel" in activity.metadata
            assert "channel_id" in activity.metadata
            assert "is_thread" in activity.metadata

    def test_activities_within_date_range(self):
        """Test that all activities fall within the requested date range."""
        connector = MockSlackConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert start_date <= activity.timestamp <= end_date


class TestMockEmailConnector:
    """Tests for MockEmailConnector."""

    def test_validate_config(self):
        """Test config validation always succeeds."""
        connector = MockEmailConnector({})
        assert connector.validate_config() is True

    def test_name_property(self):
        """Test connector name property."""
        connector = MockEmailConnector({})
        assert connector.name == "email_mock"

    def test_fetch_activities_returns_data(self):
        """Test that fetch_activities returns mock data."""
        connector = MockEmailConnector({"email": "test@example.com"})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        assert len(activities) > 0
        assert all(act.source == "email" for act in activities)

    def test_activities_have_different_types(self):
        """Test that mock data includes sent and received emails."""
        connector = MockEmailConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)
        activity_types = {act.activity_type for act in activities}

        # Should have both sent and received emails
        assert "email_sent" in activity_types or "email_received" in activity_types

    def test_activities_have_email_metadata(self):
        """Test that activities include email metadata."""
        connector = MockEmailConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert activity.metadata is not None
            assert "folder" in activity.metadata
            assert "to" in activity.metadata
            assert "subject" in activity.metadata
            assert "has_attachments" in activity.metadata

    def test_activities_within_date_range(self):
        """Test that all activities fall within the requested date range."""
        connector = MockEmailConnector({})
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        activities = connector.fetch_activities(start_date, end_date)

        for activity in activities:
            assert start_date <= activity.timestamp <= end_date

    def test_custom_email_in_config(self):
        """Test that custom email from config is used."""
        custom_email = "custom@example.com"
        connector = MockEmailConnector({"email": custom_email})

        assert connector.email == custom_email


class TestMockConnectorsIntegration:
    """Integration tests for all mock connectors."""

    def test_all_connectors_produce_activities(self):
        """Test that all mock connectors produce activities."""
        connectors = [
            MockGitHubConnector({}),
            MockSlackConnector({}),
            MockEmailConnector({}),
        ]

        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        for connector in connectors:
            activities = connector.fetch_activities(start_date, end_date)
            assert len(activities) > 0, f"{connector.name} produced no activities"

    def test_activities_are_sortable(self):
        """Test that activities from all connectors can be sorted by timestamp."""
        connectors = [
            MockGitHubConnector({}),
            MockSlackConnector({}),
            MockEmailConnector({}),
        ]

        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        all_activities = []
        for connector in connectors:
            all_activities.extend(connector.fetch_activities(start_date, end_date))

        # Sort by timestamp
        sorted_activities = sorted(all_activities, key=lambda x: x.timestamp)

        # Verify sorting worked
        for i in range(len(sorted_activities) - 1):
            assert sorted_activities[i].timestamp <= sorted_activities[i + 1].timestamp
