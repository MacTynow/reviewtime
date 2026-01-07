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
            click.echo(
                f"Warning: Unknown connector '{source_name}', skipping", err=True
            )
            continue

        try:
            connector = connector_class(source_config)
            connector.validate_config()
            connectors.append(connector)
            click.echo(f"✓ Initialized {source_name} connector")
        except Exception as e:
            click.echo(f"✗ Failed to initialize {source_name} connector: {e}", err=True)

    return connectors


# ===== CONFIG WIZARD HELPER FUNCTIONS =====


def check_existing_config(config_path: Path) -> bool:
    """Check if config exists and ask about overwriting. Returns True to proceed."""
    if config_path.exists():
        return click.confirm(
            f"Config file {config_path} already exists. Overwrite?", default=False
        )
    return True


def prompt_connector_selection() -> list[str]:
    """Ask user which connectors to enable. Returns list like ['github', 'slack']."""
    connectors_input = click.prompt(
        "Which connectors do you want to enable? (comma-separated: github,slack,email)",
        type=str,
        default="github,slack,email",
    )
    return [c.strip().lower() for c in connectors_input.split(",") if c.strip()]


def validate_connector_with_retry(
    connector_name: str, config: dict[str, Any]
) -> dict[str, Any] | None:
    """Validate connector config with retry/skip/abort options."""
    while True:
        try:
            connector_class = CONNECTOR_CLASSES[connector_name]
            connector = connector_class(config)
            click.echo("  Validating...", nl=False)
            connector.validate_config()
            click.echo(" ✓ Success")
            return config
        except Exception as e:
            click.echo(f" ✗ Failed: {e}", err=True)
            choice = click.prompt(
                "  What would you like to do?",
                type=click.Choice(["retry", "skip", "abort"], case_sensitive=False),
                default="retry",
            )
            if choice == "skip":
                return None
            elif choice == "abort":
                click.echo("Configuration cancelled.")
                sys.exit(0)
            # If retry, loop continues


def prompt_github_config(connector_type: str = "github") -> dict[str, Any] | None:
    """Collect GitHub configuration interactively."""
    is_mock = connector_type.endswith("_mock")

    click.echo("\n=== GitHub Configuration ===")
    config: dict[str, Any]
    if is_mock:
        click.echo("  (Using mock connector - no real credentials needed)")
        # Mock connectors don't need actual credentials
        config = {"enabled": True}
    else:
        token = click.prompt("GitHub Personal Access Token", hide_input=True)
        username = click.prompt("GitHub Username")
        config = {"enabled": True, "token": token, "username": username}

    if click.confirm("Filter specific repositories?", default=False):
        repos = click.prompt("Repository list (comma-separated, format: owner/repo)")
        config["repos"] = [r.strip() for r in repos.split(",") if r.strip()]

    return validate_connector_with_retry(connector_type, config)


def prompt_slack_config(connector_type: str = "slack") -> dict[str, Any] | None:
    """Collect Slack configuration interactively."""
    is_mock = connector_type.endswith("_mock")

    click.echo("\n=== Slack Configuration ===")
    config: dict[str, Any]
    if is_mock:
        click.echo("  (Using mock connector - no real credentials needed)")
        config = {"enabled": True}
    else:
        token = click.prompt("Slack User Token (starts with xoxp-)", hide_input=True)
        config = {"enabled": True, "token": token}

    if click.confirm("Filter specific channels?", default=False):
        channels = click.prompt("Channel IDs (comma-separated)")
        config["channels"] = [c.strip() for c in channels.split(",") if c.strip()]

    return validate_connector_with_retry(connector_type, config)


def prompt_email_config(connector_type: str = "email") -> dict[str, Any] | None:
    """Collect Email configuration interactively."""
    is_mock = connector_type.endswith("_mock")

    click.echo("\n=== Email Configuration ===")
    config: dict[str, Any]
    if is_mock:
        click.echo("  (Using mock connector - no real credentials needed)")
        config = {"enabled": True}
    else:
        host = click.prompt("IMAP Server Host (e.g., imap.gmail.com)")
        email = click.prompt("Email Address")
        password = click.prompt("Email Password or App Password", hide_input=True)
        port = click.prompt("IMAP Port", type=int, default=993)
        use_ssl = click.confirm("Use SSL?", default=True)

        config = {
            "enabled": True,
            "host": host,
            "email": email,
            "password": password,
            "port": port,
            "use_ssl": use_ssl,
        }

    if click.confirm("Customize folders?", default=False):
        folders = click.prompt("Folders (comma-separated)", default="INBOX,Sent")
        config["folders"] = [f.strip() for f in folders.split(",") if f.strip()]

    return validate_connector_with_retry(connector_type, config)


def prompt_anthropic_key() -> str | None:
    """Prompt for optional Anthropic API key."""
    click.echo("\n=== AI Summaries (Optional) ===")
    key = click.prompt(
        "Anthropic API Key for AI summaries (press Enter to skip)",
        default="",
        hide_input=True,
        show_default=False,
    )
    return key if key else None


def display_config_summary(config: dict) -> None:
    """Display configuration summary (without sensitive data)."""
    click.echo("\n=== Configuration Summary ===")
    for source, source_config in config.get("sources", {}).items():
        if source_config.get("enabled"):
            click.echo(f"  ✓ {source}: configured")

    if "anthropic_api_key" in config:
        click.echo("  ✓ Anthropic API key: configured")


def write_config_file(config: dict, config_path: Path) -> None:
    """Write configuration to YAML file with backup and permissions."""
    import shutil

    # Backup existing file
    if config_path.exists():
        backup = config_path.with_suffix(".yaml.backup")
        click.echo(f"  Backing up existing config to {backup}")
        shutil.copy(config_path, backup)

    # Write new config
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    # Set permissions to 0600 (owner read/write only)
    try:
        config_path.chmod(0o600)
    except Exception as e:
        click.echo(f"  Warning: Could not set file permissions: {e}", err=True)


@click.group()
def main():
    """Weekly Summary Generator - Aggregate work activities from multiple sources."""
    pass


@main.command()
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
def generate(
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
    click.echo(
        f"\nGenerating report for: {date_start.strftime('%Y-%m-%d')} to {date_end.strftime('%Y-%m-%d')}"
    )
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
        name.endswith("_mock")
        for name in cfg.get("sources", {}).keys()
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
                click.echo(
                    f"  ✓ Generated AI summaries for: {', '.join(summaries.keys())}"
                )
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
        report_path = generator.generate(
            all_activities, date_start, date_end, output, summaries
        )
        click.echo(f"✓ Report generated successfully: {report_path}")
        return 0
    except Exception as e:
        click.echo(f"✗ Error generating report: {e}", err=True)
        return 1


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="config.yaml",
    help="Output path for configuration file",
)
def config(output: Path):
    """Interactive configuration wizard."""
    try:
        click.echo("Weekly Summary Configuration Wizard")
        click.echo("=" * 50)

        # Check existing config
        if not check_existing_config(output):
            click.echo("Configuration cancelled.")
            return

        # Select connectors
        selected = prompt_connector_selection()
        if not selected:
            click.echo("No connectors selected. Exiting.")
            return

        # Build configuration
        sources_config = {}

        # Prompt for each selected connector
        for connector_name in selected:
            # Map mock connectors to their base types for prompting
            base_type = connector_name.replace("_mock", "")

            if base_type == "github":
                cfg = prompt_github_config(connector_name)
                if cfg:
                    sources_config[connector_name] = cfg
            elif base_type == "slack":
                cfg = prompt_slack_config(connector_name)
                if cfg:
                    sources_config[connector_name] = cfg
            elif base_type == "email":
                cfg = prompt_email_config(connector_name)
                if cfg:
                    sources_config[connector_name] = cfg
            else:
                click.echo(
                    f"  Warning: Unknown connector '{connector_name}', skipping",
                    err=True,
                )

        if not sources_config:
            click.echo("No connectors configured successfully.")
            return

        # Build final config
        final_config: dict[str, Any] = {"sources": sources_config}

        # Optional: Anthropic API key
        api_key = prompt_anthropic_key()
        if api_key:
            final_config["anthropic_api_key"] = api_key

        # Review and confirm
        display_config_summary(final_config)
        if not click.confirm("\nWrite this configuration?", default=True):
            click.echo("Configuration cancelled.")
            return

        # Write config file
        write_config_file(final_config, output)

        click.echo(f"\n✓ Configuration saved to {output}")
        click.echo("\nNext steps:")
        click.echo("  Run 'weekly-summary generate' to create your first report")

    except KeyboardInterrupt:
        click.echo("\n\nConfiguration cancelled. No changes were made.")
        sys.exit(0)


if __name__ == "__main__":
    main()
