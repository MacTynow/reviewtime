"""AI-powered summarizer for generating weekly activity summaries."""

import os

from anthropic import Anthropic
from anthropic.types import TextBlock

from .connectors.base import Activity


class ActivitySummarizer:
    """Generate AI summaries of weekly activities."""

    def __init__(self, api_key: str | None = None, mock: bool = False):
        """
        Initialize the summarizer.

        Args:
            api_key: Anthropic API key. If not provided, will try to read from ANTHROPIC_API_KEY env var.
            mock: If True, use mock summaries instead of real API calls.
        """
        self.mock = mock
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = (
            Anthropic(api_key=self.api_key) if self.api_key and not mock else None
        )

    def is_available(self) -> bool:
        """Check if summarization is available (API key configured or mock mode)."""
        return self.client is not None or self.mock

    def generate_summary(
        self,
        activities: list[Activity],
        start_date: str,
        end_date: str,
    ) -> dict[str, str]:
        """
        Generate AI-powered summaries for activities by source.

        Args:
            activities: List of activities to summarize
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)

        Returns:
            Dictionary with source names as keys and summaries as values
        """
        if not self.is_available():
            return {}

        # Group activities by source
        by_source: dict[str, list[Activity]] = {}
        for activity in activities:
            if activity.source not in by_source:
                by_source[activity.source] = []
            by_source[activity.source].append(activity)

        summaries = {}

        # Generate summary for each source
        for source, source_activities in by_source.items():
            if source in ["github", "slack"]:  # Only summarize github and slack
                summary = self._summarize_source(
                    source, source_activities, start_date, end_date
                )
                if summary:
                    summaries[source] = summary

        return summaries

    def _summarize_source(
        self,
        source: str,
        activities: list[Activity],
        start_date: str,
        end_date: str,
    ) -> str:
        """Generate summary for a specific source."""
        if not activities:
            return ""

        # Return mock summary if in mock mode
        if self.mock:
            return self._get_mock_summary(source, len(activities))

        # Prepare activity data for the prompt
        activity_text = self._format_activities_for_summary(activities, source)

        # Create appropriate prompt based on source
        if source == "github":
            prompt = self._create_github_prompt(activity_text, start_date, end_date)
        elif source == "slack":
            prompt = self._create_slack_prompt(activity_text, start_date, end_date)
        else:
            return ""

        try:
            # Ensure client is not None (checked in is_available)
            if self.client is None:
                return ""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            if message.content and len(message.content) > 0:
                first_block = message.content[0]
                # Only TextBlock has the text attribute
                if isinstance(first_block, TextBlock):
                    return first_block.text.strip()
            return ""
        except Exception as e:
            # Silently fail if API call doesn't work
            print(f"Warning: Failed to generate {source} summary: {e}")
            return ""

    def _get_mock_summary(self, source: str, activity_count: int) -> str:
        """Generate mock summary for testing."""
        if source == "github":
            return f"""This week's development work focused on three main areas: performance optimization, security improvements, and feature enhancements.

The team made significant progress on the backend infrastructure, implementing Redis caching for user profiles which resulted in a 40% improvement in API response times. Several critical bugs were addressed, including an authentication issue that prevented users with special characters in their passwords from logging in, and a memory leak in the websocket handler that was affecting long-running connections.

On the feature development side, work continued on the email notification system with a pull request successfully merged, and the API response format standardization effort moved forward. The team also improved error messaging throughout the API to make them more user-friendly and actionable. Overall, {activity_count} activities were completed across multiple repositories, demonstrating good velocity and focus on both immediate fixes and longer-term improvements."""

        elif source == "slack":
            return f"""Team communications this week centered around technical architecture decisions, operational improvements, and cross-functional collaboration.

Key technical discussions included architecture proposals for the payment processing microservices, debates about caching strategies (Redis vs Memcached for session storage), and API design reviews. The engineering team shared important updates on performance optimization results and coordinated on database migration strategies. An incident response highlighted the team's operational maturity, with quick identification and resolution of a database connection pool issue that was affecting API response times.

The team maintained strong collaboration patterns through regular standups, code review discussions in the #pull-requests channel, and productive cross-functional sync with product on Q2 roadmap feasibility. With {activity_count} messages across multiple channels, the week showed healthy engagement across backend development, DevOps, and product alignment discussions."""

        return ""

    def _format_activities_for_summary(
        self, activities: list[Activity], source: str
    ) -> str:
        """Format activities into text for summarization."""
        lines = []

        if source == "github":
            # Group by repo and type
            by_repo: dict[str, dict[str, list[Activity]]] = {}
            for activity in activities:
                repo = (
                    activity.metadata.get("repo", "unknown")
                    if activity.metadata
                    else "unknown"
                )
                if repo not in by_repo:
                    by_repo[repo] = {}
                if activity.activity_type not in by_repo[repo]:
                    by_repo[repo][activity.activity_type] = []
                by_repo[repo][activity.activity_type].append(activity)

            for repo, types in by_repo.items():
                lines.append(f"\nRepository: {repo}")
                for activity_type, acts in types.items():
                    lines.append(f"  {activity_type}:")
                    for act in acts:
                        lines.append(f"    - {act.title}: {act.description}")

        elif source == "slack":
            # Group by channel
            by_channel: dict[str, list[Activity]] = {}
            for activity in activities:
                channel = (
                    activity.metadata.get("channel", "unknown")
                    if activity.metadata
                    else "unknown"
                )
                if channel not in by_channel:
                    by_channel[channel] = []
                by_channel[channel].append(activity)

            for channel, acts in by_channel.items():
                lines.append(f"\n#{channel}:")
                for act in acts:
                    lines.append(f"  - {act.title}: {act.description}")

        return "\n".join(lines)

    def _create_github_prompt(
        self, activity_text: str, start_date: str, end_date: str
    ) -> str:
        """Create prompt for GitHub summary."""
        return f"""Summarize the following GitHub activities from {start_date} to {end_date}.

Focus on:
- Key technical work and accomplishments
- Important features or fixes delivered
- Overall themes or focus areas
- Notable contributions

Write a concise 2-3 paragraph summary that gives a clear picture of the week's work.
Use a professional but conversational tone.

Activities:
{activity_text}

Summary:"""

    def _create_slack_prompt(
        self, activity_text: str, start_date: str, end_date: str
    ) -> str:
        """Create prompt for Slack summary."""
        return f"""Summarize the following Slack discussions and communications from {start_date} to {end_date}.

Focus on:
- Key topics discussed across channels
- Important decisions or proposals
- Team collaborations and cross-functional work
- Recurring themes or focus areas

Write a concise 2-3 paragraph summary that captures the essence of the week's discussions.
Use a professional but conversational tone.

Messages:
{activity_text}

Summary:"""
