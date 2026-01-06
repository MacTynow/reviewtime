# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
# Install dependencies
uv add <dep>
```

### Building the Website
```bash
# Build Hugo website from reports
make build

# Generate mock report + build + serve website (all-in-one)
make website

# Serve website locally for development
make serve
# Visit http://localhost:1313 to view
```

### Testing
```bash
# Run all tests
uv run pytest

# Run all tests with verbose output
uv run pytest -v

# Run a single test file
uv run pytest tests/test_activity.py

# Run tests with coverage
uv run pytest --cov=src
```

### Linting
```bash
# Run linter (ruff)
uv run ruff check src tests

# Fix linting issues automatically
uv run ruff check --fix src tests

# Format code with black
uv run black src tests
```

### Running
```bash
# Quick start with Makefile (recommended)
make help                    # Show all available commands
make generate-mock           # Generate report with mock data
make website                 # Generate + build + serve (all-in-one)

# Or use the CLI directly
# Generate a weekly summary with mock data (no authentication required!)
uv run weekly-summary --config config.mock.yaml

# Generate report for specific date range with mock data
uv run weekly-summary --config config.mock.yaml --start-date 2024-01-01 --end-date 2024-01-07

# Generate report with real APIs (requires config.yaml with tokens)
uv run weekly-summary --config config.yaml

# Custom output directory
uv run weekly-summary --config config.mock.yaml --output-dir my-reports
```

## Architecture Overview

### Project Structure
This project uses Python and uv.
This tool pulls emails, slack logs, PR reviews and commits from Github to write a summary of work done during the week. The summary will be output as an markdown file.
The output can be built as a static website with hugo to be able to be browsed chronologically.
There will be a module/class for each system. It needs to be easy to add a new system to connect to the tool.

Write unit tests for everything you add.

Prompt the user as required for manual tests.

### Key Components

**Connectors** (`src/weekly_summary/connectors/`)
- `BaseConnector`: Abstract base class for all data sources
- `GitHubConnector`: Fetches commits, PRs, and reviews from GitHub
- `SlackConnector`: Fetches messages from Slack channels
- `EmailConnector`: Fetches emails via IMAP
- `Mock*Connector`: Mock implementations with fake data for testing

**Report Generator** (`src/weekly_summary/report/`)
- Aggregates activities from all sources
- Generates markdown reports grouped by source and timeline
- Includes statistics and summaries

**CLI** (`src/weekly_summary/cli.py`)
- Main entry point for the tool
- Handles configuration loading and connector initialization
- Orchestrates data fetching and report generation

### Data Flow

1. CLI loads configuration from YAML file
2. CLI initializes connectors based on config (GitHub, Slack, Email, or mocks)
3. Each connector validates its configuration
4. CLI requests activities from each connector for the date range
5. Connectors fetch and transform data into standardized `Activity` objects
6. ReportGenerator aggregates all activities
7. Report is generated as markdown and saved to disk

### Important Patterns

**Plugin Architecture**: New data sources can be added by:
1. Creating a class that extends `BaseConnector`
2. Implementing `fetch_activities()`, `validate_config()`, and `name` property
3. Registering the connector in `CONNECTOR_CLASSES` in `cli.py`

**Configuration-driven**: All connectors are configured via YAML, making it easy to enable/disable sources or switch between real and mock data.

**Mock Data for Testing**: The project includes mock connectors that generate realistic fake data, allowing you to test the full workflow without requiring API tokens or authentication.

## Testing & Development

### Using Mock Data

For development and testing without API credentials:

1. Use the provided `config.mock.yaml` configuration
2. Mock connectors generate realistic fake data for:
   - GitHub: commits, PRs, and reviews
   - Slack: channel messages
   - Email: sent and received emails
3. No authentication required - great for demos and testing!

### Adding a New Connector

1. Create a new file in `src/weekly_summary/connectors/`
2. Extend `BaseConnector` and implement required methods
3. Add connector to `CONNECTOR_CLASSES` in `cli.py`
4. Add configuration example to `config.example.yaml`
5. Write unit tests in `tests/`

## Additional Notes

- Reports are generated in markdown format in the `reports/` directory
- Each report filename includes the date range: `weekly-summary_YYYY-MM-DD_to_YYYY-MM-DD.md`
- The tool can be used to build a static website with Hugo by organizing reports chronologically
- All dates are handled in UTC timezone
