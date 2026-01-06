"""Command-line interface for weekly summary generator."""

import sys
from pathlib import Path
from typing import Any

import click
import yaml

from .connectors.base import BaseConnector
from .connectors.email import EmailConnector
from .connectors.github import GitHubConnector
from .connectors.slack import SlackConnector
from .connectors.mock import MockEmailConnector, MockGitHubConnector, MockSlackConnector
from .report.generator import ReportGenerator
from .summarizer import ActivitySummarizer
from .utils.date_utils import parse_date_range


CONNECTOR_CLASSES = {
    "github": GitHubConnector,
    "slack": SlackConnector,
    "email": EmailConnector,
    "github_mock": MockGitHubConnector,
    "slack_mock": MockSlackConnector,
    "email_mock": MockEmailConnector,
}


def load_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def initialize_connectors(config: dict[str, Any]) -> list[BaseConnector]:
    """Initialize connectors based on configuration."""
    connectors = []

    for source_name, source_config in config.get("sources", {}).items():
        if not source_config.get("enabled", True):
            continue

        connector_class = CONNECTOR_CLASSES.get(source_name)
        if not connector_class:
            click.echo(f"Warning: Unknown connector '{source_name}', skipping", err=True)
            continue

        try:
            connector = connector_class(source_config)
            connector.validate_config()
            connectors.append(connector)
            click.echo(f"✓ Initialized {source_name} connector")
        except Exception as e:
            click.echo(f"✗ Failed to initialize {source_name} connector: {e}", err=True)

    return connectors


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to configuration file",
)
@click.option(
    "--start-date",
    "-s",
    type=str,
    help="Start date (YYYY-MM-DD). Defaults to last Monday",
)
@click.option(
    "--end-date",
    "-e",
    type=str,
    help="End date (YYYY-MM-DD). Defaults to last Sunday",
)
@click.option(
    "--output",
    "-o",
    type=str,
    help="Output filename (relative to output directory)",
)
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(path_type=Path),
    default="reports",
    help="Output directory for reports",
)
def main(
    config: Path,
    start_date: str | None,
    end_date: str | None,
    output: str | None,
    output_dir: Path,
):
    """
    Generate a weekly summary report from GitHub, Slack, and Email.

    By default, generates a report for the last complete week (Monday to Sunday).
    """
    click.echo("Weekly Summary Generator")
    click.echo("=" * 50)

    # Load configuration
    try:
        cfg = load_config(config)
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)

    # Parse date range
    date_start, date_end = parse_date_range(start_date, end_date)
    click.echo(f"\nGenerating report for: {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}")
    click.echo()

    # Initialize connectors
    click.echo("Initializing connectors...")
    connectors = initialize_connectors(cfg)

    if not connectors:
        click.echo("No connectors were successfully initialized. Exiting.", err=True)
        sys.exit(1)

    click.echo()

    # Fetch activities
    click.echo("Fetching activities...")
    all_activities = []

    for connector in connectors:
        try:
            click.echo(f"  Fetching from {connector.name}...")
            activities = connector.fetch_activities(date_start, date_end)
            all_activities.extend(activities)
            click.echo(f"  ✓ Found {len(activities)} activities from {connector.name}")
        except Exception as e:
            click.echo(f"  ✗ Error fetching from {connector.name}: {e}", err=True)

    click.echo()
    click.echo(f"Total activities collected: {len(all_activities)}")

    if not all_activities:
        click.echo("\nNo activities found for the specified date range.")
        return 0

    # Generate AI summaries if enabled
    summaries = {}
    use_mock_summaries = any(
        name.endswith("_mock") for name in cfg.get("sources", {}).keys()
        if cfg.get("sources", {}).get(name, {}).get("enabled", False)
    )

    click.echo("\nGenerating summaries...")
    summarizer = ActivitySummarizer(mock=use_mock_summaries)
    if summarizer.is_available():
        try:
            summaries = summarizer.generate_summary(
                all_activities,
                date_start.strftime("%Y-%m-%d"),
                date_end.strftime("%Y-%m-%d"),
            )
            if summaries:
                click.echo(f"  ✓ Generated AI summaries for: {', '.join(summaries.keys())}")
            else:
                click.echo("  ℹ No summaries generated")
        except Exception as e:
            click.echo(f"  ✗ Error generating summaries: {e}", err=True)
    else:
        click.echo("  ℹ Summaries disabled (set ANTHROPIC_API_KEY to enable)")

    # Generate report
    click.echo("\nGenerating report...")
    generator = ReportGenerator(output_dir)

    try:
        report_path = generator.generate(all_activities, date_start, date_end, output, summaries)
        click.echo(f"✓ Report generated successfully: {report_path}")
        return 0
    except Exception as e:
        click.echo(f"✗ Error generating report: {e}", err=True)
        return 1


if __name__ == "__main__":
    main()
