"""Markdown report generator."""

from datetime import datetime
from pathlib import Path

from ..connectors.base import Activity


class ReportGenerator:
    """Generate markdown reports from activities."""

    def __init__(self, output_dir: Path | str = "reports"):
        """
        Initialize the report generator.

        Args:
            output_dir: Directory where reports will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        activities: list[Activity],
        start_date: datetime,
        end_date: datetime,
        output_file: str | None = None,
        summaries: dict[str, str] | None = None,
    ) -> Path:
        """
        Generate a markdown report from activities.

        Args:
            activities: List of activities to include in the report
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            output_file: Optional custom output filename
            summaries: Optional AI-generated summaries by source

        Returns:
            Path to the generated report file
        """
        if not output_file:
            # Generate filename from date range
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            output_file = f"weekly-summary_{start_str}_to_{end_str}.md"

        report_path = self.output_dir / output_file

        # Sort activities by timestamp
        sorted_activities = sorted(activities)

        # Group activities by source
        activities_by_source: dict[str, list[Activity]] = {}
        for activity in sorted_activities:
            if activity.source not in activities_by_source:
                activities_by_source[activity.source] = []
            activities_by_source[activity.source].append(activity)

        # Group activities by day
        activities_by_day: dict[str, list[Activity]] = {}
        for activity in sorted_activities:
            day_key = activity.timestamp.strftime("%Y-%m-%d")
            if day_key not in activities_by_day:
                activities_by_day[day_key] = []
            activities_by_day[day_key].append(activity)

        # Generate markdown content
        content = self._generate_markdown(
            sorted_activities,
            activities_by_source,
            activities_by_day,
            start_date,
            end_date,
            summaries or {},
        )

        # Write to file
        report_path.write_text(content)

        return report_path

    def _generate_markdown(
        self,
        all_activities: list[Activity],
        by_source: dict[str, list[Activity]],
        by_day: dict[str, list[Activity]],
        start_date: datetime,
        end_date: datetime,
        summaries: dict[str, str],
    ) -> str:
        """Generate the markdown content."""
        lines = []

        # Hugo front matter
        lines.append("---")
        lines.append(
            f"title: \"Weekly Summary: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}\""
        )
        lines.append(f"date: {start_date.strftime('%Y-%m-%d')}")
        lines.append(f"endDate: {end_date.strftime('%Y-%m-%d')}")
        lines.append(f"totalActivities: {len(all_activities)}")

        # Add source counts
        source_counts = {
            source: len(activities) for source, activities in by_source.items()
        }
        lines.append("sources:")
        for source, count in source_counts.items():
            lines.append(f"  {source}: {count}")

        lines.append("draft: false")
        lines.append("---")
        lines.append("")

        # Header
        lines.append(
            f"# Weekly Summary: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        )
        lines.append("")
        lines.append(
            f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*"
        )
        lines.append("")

        # AI-generated summaries (if available)
        if summaries:
            lines.append("## 📝 Summary")
            lines.append("")

            # GitHub summary
            if "github" in summaries and summaries["github"]:
                lines.append("### Development Work")
                lines.append("")
                lines.append(summaries["github"])
                lines.append("")

            # Slack summary
            if "slack" in summaries and summaries["slack"]:
                lines.append("### Team Discussions & Collaboration")
                lines.append("")
                lines.append(summaries["slack"])
                lines.append("")

            lines.append("---")
            lines.append("")

        # Summary statistics
        lines.append("## 📊 Activity Summary")
        lines.append("")
        lines.append(f"**Total Activities:** {len(all_activities)}")
        lines.append("")

        for source, activities in by_source.items():
            lines.append(f"- **{source.title()}:** {len(activities)} activities")

        lines.append("")

        # Activities by source
        lines.append("## Activities by Source")
        lines.append("")

        for source, activities in by_source.items():
            lines.append(f"### {source.title()}")
            lines.append("")

            # Group by activity type
            by_type: dict[str, list[Activity]] = {}
            for activity in activities:
                if activity.activity_type not in by_type:
                    by_type[activity.activity_type] = []
                by_type[activity.activity_type].append(activity)

            for activity_type, typed_activities in by_type.items():
                lines.append(
                    f"#### {activity_type.replace('_', ' ').title()} ({len(typed_activities)})"
                )
                lines.append("")

                for activity in typed_activities:
                    lines.append(self._format_activity(activity))

                lines.append("")

        # Timeline view (activities by day)
        lines.append("## Timeline")
        lines.append("")

        for day, activities in sorted(by_day.items()):
            day_date = datetime.strptime(day, "%Y-%m-%d")
            lines.append(f"### {day_date.strftime('%A, %B %d, %Y')}")
            lines.append("")

            for activity in activities:
                lines.append(self._format_activity(activity, include_source=True))

            lines.append("")

        return "\n".join(lines)

    def _format_activity(self, activity: Activity, include_source: bool = False) -> str:
        """Format a single activity as markdown."""
        time_str = activity.timestamp.strftime("%I:%M %p")

        # Build the activity line
        parts = [f"- **{time_str}**"]

        if include_source:
            parts.append(f"[{activity.source}]")

        if activity.url:
            parts.append(f"[{activity.title}]({activity.url})")
        else:
            parts.append(activity.title)

        line = " ".join(parts)

        # Add description if it exists and is meaningful
        if activity.description and activity.description.strip():
            # Indent description
            desc_lines = activity.description.split("\n")
            formatted_desc = "\n  ".join(
                [f"> {line.strip()}" for line in desc_lines if line.strip()]
            )
            if formatted_desc:
                line += f"\n  {formatted_desc}"

        return line
