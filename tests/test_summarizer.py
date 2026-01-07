"""Tests for ActivitySummarizer."""

from datetime import datetime, timezone

from weekly_summary.connectors.base import Activity
from weekly_summary.summarizer import ActivitySummarizer


class TestActivitySummarizer:
    """Tests for ActivitySummarizer."""

    def test_mock_mode_is_available(self):
        """Test that mock mode is available without API key."""
        summarizer = ActivitySummarizer(mock=True)
        assert summarizer.is_available() is True

    def test_no_api_key_not_available(self, monkeypatch):
        """Test that summarizer is not available without API key."""
        # Ensure no API key in environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        summarizer = ActivitySummarizer(api_key=None, mock=False)
        assert summarizer.is_available() is False

    def test_with_api_key_is_available(self):
        """Test that summarizer is available with API key."""
        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.is_available() is True

    def test_generate_summary_mock_mode(self):
        """Test generating summaries in mock mode."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed authentication bug",
                source="github",
                activity_type="commit",
                url="https://github.com/test/repo/commit/123",
                metadata={"repo": "test/repo", "sha": "123"},
            ),
            Activity(
                timestamp=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc),
                title="Discussed feature",
                description="Team discussion about new feature",
                source="slack",
                activity_type="message",
                url="https://slack.com/archives/123/p456",
                metadata={"channel": "engineering", "channel_id": "C123"},
            ),
        ]

        summaries = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")

        assert "github" in summaries
        assert "slack" in summaries
        assert len(summaries["github"]) > 0
        assert len(summaries["slack"]) > 0
        assert (
            "performance optimization" in summaries["github"].lower()
            or "development work" in summaries["github"].lower()
        )
        assert (
            "team communications" in summaries["slack"].lower()
            or "discussions" in summaries["slack"].lower()
        )

    def test_generate_summary_no_activities(self):
        """Test generating summaries with no activities."""
        summarizer = ActivitySummarizer(mock=True)

        summaries = summarizer.generate_summary([], "2024-01-01", "2024-01-07")

        assert summaries == {}

    def test_generate_summary_only_github(self):
        """Test generating summaries with only GitHub activities."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed authentication bug",
                source="github",
                activity_type="commit",
                url="https://github.com/test/repo/commit/123",
                metadata={"repo": "test/repo", "sha": "123"},
            ),
        ]

        summaries = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")

        assert "github" in summaries
        assert "slack" not in summaries

    def test_generate_summary_only_slack(self):
        """Test generating summaries with only Slack activities."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc),
                title="Discussed feature",
                description="Team discussion about new feature",
                source="slack",
                activity_type="message",
                url="https://slack.com/archives/123/p456",
                metadata={"channel": "engineering", "channel_id": "C123"},
            ),
        ]

        summaries = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")

        assert "slack" in summaries
        assert "github" not in summaries

    def test_generate_summary_with_email(self):
        """Test that email activities are not summarized."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Sent email",
                description="Project update",
                source="email",
                activity_type="email_sent",
                url=None,
                metadata={"to": ["team@example.com"]},
            ),
        ]

        summaries = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")

        # Email should not be summarized
        assert "email" not in summaries

    def test_get_mock_summary_github(self):
        """Test mock summary for GitHub."""
        summarizer = ActivitySummarizer(mock=True)

        summary = summarizer._get_mock_summary("github", 10)

        assert len(summary) > 0
        assert "10 activities" in summary
        assert "development work" in summary.lower()

    def test_get_mock_summary_slack(self):
        """Test mock summary for Slack."""
        summarizer = ActivitySummarizer(mock=True)

        summary = summarizer._get_mock_summary("slack", 15)

        assert len(summary) > 0
        assert "15 messages" in summary
        assert "team communications" in summary.lower()

    def test_get_mock_summary_unknown_source(self):
        """Test mock summary for unknown source returns empty."""
        summarizer = ActivitySummarizer(mock=True)

        summary = summarizer._get_mock_summary("unknown", 5)

        assert summary == ""

    def test_format_activities_github(self):
        """Test formatting GitHub activities for summarization."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed auth bug",
                source="github",
                activity_type="commit",
                url="https://github.com/test/repo/commit/123",
                metadata={"repo": "test/repo", "sha": "123"},
            ),
            Activity(
                timestamp=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc),
                title="Add feature",
                description="Added caching",
                source="github",
                activity_type="commit",
                url="https://github.com/test/repo/commit/456",
                metadata={"repo": "test/repo", "sha": "456"},
            ),
        ]

        formatted = summarizer._format_activities_for_summary(activities, "github")

        assert "Repository: test/repo" in formatted
        assert "Fix bug" in formatted
        assert "Add feature" in formatted

    def test_format_activities_slack(self):
        """Test formatting Slack activities for summarization."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc),
                title="Discussed feature",
                description="Team discussion",
                source="slack",
                activity_type="message",
                url="https://slack.com/archives/123/p456",
                metadata={"channel": "engineering", "channel_id": "C123"},
            ),
        ]

        formatted = summarizer._format_activities_for_summary(activities, "slack")

        assert "#engineering:" in formatted
        assert "Discussed feature" in formatted

    def test_create_github_prompt(self):
        """Test creating GitHub prompt."""
        summarizer = ActivitySummarizer(mock=True)

        prompt = summarizer._create_github_prompt(
            "test activities", "2024-01-01", "2024-01-07"
        )

        assert "2024-01-01" in prompt
        assert "2024-01-07" in prompt
        assert "test activities" in prompt
        assert "GitHub" in prompt or "github" in prompt.lower()

    def test_create_slack_prompt(self):
        """Test creating Slack prompt."""
        summarizer = ActivitySummarizer(mock=True)

        prompt = summarizer._create_slack_prompt(
            "test messages", "2024-01-01", "2024-01-07"
        )

        assert "2024-01-01" in prompt
        assert "2024-01-07" in prompt
        assert "test messages" in prompt
        assert "Slack" in prompt or "slack" in prompt.lower()

    def test_summarizer_not_available_returns_empty(self):
        """Test that unavailable summarizer returns empty dict."""
        summarizer = ActivitySummarizer(api_key=None, mock=False)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed bug",
                source="github",
                activity_type="commit",
                url="https://github.com/test/repo/commit/123",
                metadata={"repo": "test/repo"},
            ),
        ]

        summaries = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")

        assert summaries == {}

    def test_summarize_source_with_empty_activities(self):
        """Test summarizing a source with empty activities list."""
        summarizer = ActivitySummarizer(mock=True)

        result = summarizer._summarize_source("github", [], "2024-01-01", "2024-01-07")

        assert result == ""

    def test_summarize_source_unknown_type(self):
        """Test summarizing unknown source type."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Test",
                description="Test activity",
                source="unknown",
                activity_type="test",
                url=None,
                metadata={},
            ),
        ]

        result = summarizer._summarize_source(
            "unknown", activities, "2024-01-01", "2024-01-07"
        )

        assert result == ""

    def test_format_activities_with_no_metadata(self):
        """Test formatting activities without metadata."""
        summarizer = ActivitySummarizer(mock=True)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="No metadata",
                description="Activity without metadata",
                source="github",
                activity_type="commit",
                url=None,
                metadata=None,
            ),
        ]

        formatted = summarizer._format_activities_for_summary(activities, "github")

        assert "unknown" in formatted.lower()  # Should use "unknown" for missing repo

    def test_summarize_source_not_available(self, monkeypatch):
        """Test _summarize_source returns empty when summarizer not available."""
        # Ensure no API key
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        summarizer = ActivitySummarizer(api_key=None, mock=False)

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Test",
                description="Test activity",
                source="github",
                activity_type="commit",
                url=None,
                metadata={"repo": "test/repo"},
            ),
        ]

        # Since summarizer is not available, generate_summary should return empty
        result = summarizer.generate_summary(activities, "2024-01-01", "2024-01-07")
        assert result == {}


class TestSummarizerAPIIntegration:
    """Tests for summarizer API integration (mocked)."""

    def test_summarize_source_api_success(self):
        """Test _summarize_source with mocked API success."""
        from unittest.mock import patch, MagicMock
        from anthropic.types import TextBlock

        # Create a mock Message response
        mock_message = MagicMock()
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Test summary generated by API"
        mock_message.content = [mock_text_block]

        # Create summarizer with API key
        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.client is not None

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed auth bug",
                source="github",
                activity_type="commit",
                url=None,
                metadata={"repo": "test/repo"},
            ),
        ]

        # Mock the API call
        with patch.object(
            summarizer.client.messages, "create", return_value=mock_message
        ):
            result = summarizer._summarize_source(
                "github", activities, "2024-01-01", "2024-01-07"
            )

            assert result == "Test summary generated by API"

    def test_summarize_source_api_error(self):
        """Test _summarize_source handles API errors gracefully."""
        from unittest.mock import patch

        # Create summarizer with API key
        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.client is not None

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed auth bug",
                source="github",
                activity_type="commit",
                url=None,
                metadata={"repo": "test/repo"},
            ),
        ]

        # Mock the API call to raise an exception
        with patch.object(
            summarizer.client.messages, "create", side_effect=Exception("API Error")
        ):
            result = summarizer._summarize_source(
                "github", activities, "2024-01-01", "2024-01-07"
            )

            # Should return empty string on error
            assert result == ""

    def test_summarize_source_empty_response(self):
        """Test _summarize_source handles empty API response."""
        from unittest.mock import patch, MagicMock

        # Create a mock Message response with empty content
        mock_message = MagicMock()
        mock_message.content = []

        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.client is not None

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed auth bug",
                source="github",
                activity_type="commit",
                url=None,
                metadata={"repo": "test/repo"},
            ),
        ]

        with patch.object(
            summarizer.client.messages, "create", return_value=mock_message
        ):
            result = summarizer._summarize_source(
                "github", activities, "2024-01-01", "2024-01-07"
            )

            assert result == ""

    def test_summarize_source_slack_api(self):
        """Test _summarize_source for Slack with mocked API."""
        from unittest.mock import patch, MagicMock
        from anthropic.types import TextBlock

        mock_message = MagicMock()
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Slack summary from API"
        mock_message.content = [mock_text_block]

        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.client is not None

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc),
                title="Team discussion",
                description="Discussed roadmap",
                source="slack",
                activity_type="message",
                url=None,
                metadata={"channel": "engineering"},
            ),
        ]

        with patch.object(
            summarizer.client.messages, "create", return_value=mock_message
        ):
            result = summarizer._summarize_source(
                "slack", activities, "2024-01-01", "2024-01-07"
            )

            assert result == "Slack summary from API"

    def test_summarize_source_non_textblock_response(self):
        """Test _summarize_source handles non-TextBlock content."""
        from unittest.mock import patch, MagicMock

        # Create a mock with content that isn't a TextBlock
        mock_message = MagicMock()
        mock_tool_use = MagicMock()  # Not a TextBlock
        mock_tool_use.text = None  # Would raise AttributeError if accessed
        del mock_tool_use.text  # Remove text attribute
        mock_message.content = [mock_tool_use]

        summarizer = ActivitySummarizer(api_key="test-key", mock=False)
        assert summarizer.client is not None

        activities = [
            Activity(
                timestamp=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                title="Fix bug",
                description="Fixed bug",
                source="github",
                activity_type="commit",
                url=None,
                metadata={"repo": "test/repo"},
            ),
        ]

        with patch.object(
            summarizer.client.messages, "create", return_value=mock_message
        ):
            result = summarizer._summarize_source(
                "github", activities, "2024-01-01", "2024-01-07"
            )

            # Should return empty since content isn't TextBlock
            assert result == ""
