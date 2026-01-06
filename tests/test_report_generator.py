"""Tests for report generator."""

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from weekly_summary.connectors.base import Activity
from weekly_summary.report.generator import ReportGenerator


@pytest.fixture
def sample_activities():
    """Create sample activities for testing."""
    base_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

    return [
        Activity(
            timestamp=base_time,
            title="Commit to repo",
            description="Fix bug",
            source="github",
            activity_type="commit",
            url="https://github.com/test/repo/commit/123",
        ),
        Activity(
            timestamp=base_time.replace(hour=14),
            title="Message in #general",
            description="Discussed the new feature",
            source="slack",
            activity_type="message",
        ),
        Activity(
            timestamp=base_time.replace(hour=16),
            title="Sent email",
            description="Follow up on meeting",
            source="email",
            activity_type="email_sent",
        ),
    ]


def test_report_generator_creates_directory():
    """Test that ReportGenerator creates output directory."""
    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "reports"
        ReportGenerator(output_dir)

        assert output_dir.exists()
        assert output_dir.is_dir()


def test_generate_report(sample_activities):
    """Test generating a basic report."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate(sample_activities, start_date, end_date)

        assert report_path.exists()
        assert report_path.suffix == ".md"

        content = report_path.read_text()

        # Check that report contains expected sections
        assert "# Weekly Summary" in content
        assert "## 📊 Activity Summary" in content or "## Summary" in content
        assert "## Activities by Source" in content
        assert "## Timeline" in content


def test_report_content_includes_activities(sample_activities):
    """Test that generated report includes all activities."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate(sample_activities, start_date, end_date)
        content = report_path.read_text()

        # Check that each activity appears in the report
        assert "Commit to repo" in content
        assert "Message in #general" in content
        assert "Sent email" in content

        # Check sources are mentioned
        assert "github" in content.lower()
        assert "slack" in content.lower()
        assert "email" in content.lower()


def test_report_statistics(sample_activities):
    """Test that report includes correct statistics."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate(sample_activities, start_date, end_date)
        content = report_path.read_text()

        # Check total count
        assert "**Total Activities:** 3" in content


def test_custom_output_filename(sample_activities):
    """Test using a custom output filename."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate(sample_activities, start_date, end_date, "custom-report.md")

        assert report_path.name == "custom-report.md"


def test_empty_activities_list():
    """Test generating report with no activities."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate([], start_date, end_date)

        assert report_path.exists()
        content = report_path.read_text()

        # Should still have structure but no activities
        assert "**Total Activities:** 0" in content


def test_generate_report_with_summaries(sample_activities):
    """Test generating a report with AI summaries."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        summaries = {
            "github": "This week focused on bug fixes and new features.",
            "slack": "Team discussed architecture and planning.",
        }

        report_path = generator.generate(sample_activities, start_date, end_date, summaries=summaries)

        assert report_path.exists()
        content = report_path.read_text()

        # Check that summaries are included
        assert "## 📝 Summary" in content
        assert "### Development Work" in content
        assert "This week focused on bug fixes and new features." in content
        assert "### Team Discussions & Collaboration" in content
        assert "Team discussed architecture and planning." in content


def test_generate_report_with_github_summary_only(sample_activities):
    """Test generating a report with only GitHub summary."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        summaries = {
            "github": "GitHub work summary.",
        }

        report_path = generator.generate(sample_activities, start_date, end_date, summaries=summaries)
        content = report_path.read_text()

        assert "## 📝 Summary" in content
        assert "### Development Work" in content
        assert "GitHub work summary." in content
        assert "### Team Discussions & Collaboration" not in content


def test_generate_report_with_slack_summary_only(sample_activities):
    """Test generating a report with only Slack summary."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        summaries = {
            "slack": "Slack discussion summary.",
        }

        report_path = generator.generate(sample_activities, start_date, end_date, summaries=summaries)
        content = report_path.read_text()

        assert "## 📝 Summary" in content
        assert "### Team Discussions & Collaboration" in content
        assert "Slack discussion summary." in content
        assert "### Development Work" not in content


def test_generate_report_with_empty_summaries(sample_activities):
    """Test generating a report with empty summaries dict."""
    with TemporaryDirectory() as tmpdir:
        generator = ReportGenerator(tmpdir)

        start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 7, 23, 59, 59, tzinfo=timezone.utc)

        report_path = generator.generate(sample_activities, start_date, end_date, summaries={})
        content = report_path.read_text()

        # Should not have summary section
        assert "## 📝 Summary" not in content
        # But should have activity summary
        assert "## 📊 Activity Summary" in content
