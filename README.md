# Weekly Summary Generator

A Python CLI tool that aggregates your work activities from GitHub, Slack, and Email into beautiful weekly summary reports. Perfect for status updates, performance reviews, or simply tracking what you accomplished.

## Features

- **Multi-Source Integration**: Pulls data from GitHub (commits, PRs, reviews), Slack (messages), and Email (IMAP)
- **AI-Powered Summaries**: Automatically generates executive summaries of your work using Claude AI
- **Smart Filtering**: Target specific repos in GitHub and channels in Slack to reduce noise
- **Markdown Reports**: Generates clean, organized markdown files with statistics and timelines
- **Mock Data Mode**: Test the tool without any API credentials using realistic fake data
- **Flexible Date Ranges**: Generate reports for any date range, defaults to last complete week
- **Hugo-Ready**: Output format works seamlessly with Hugo static site generator for browsing reports chronologically

## Quick Start with Mock Data

Try the tool immediately without any setup or authentication:

```bash
# Install dependencies
uv sync

# Generate a sample report with mock data (no credentials needed!)
uv run weekly-summary --config config.mock.yaml --start-date 2024-01-01 --end-date 2024-01-07

# View the generated report
cat reports/weekly-summary_2024-01-01_to_2024-01-07.md
```

This generates a realistic report with fake GitHub commits, Slack messages, and emails - perfect for testing!

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Install dependencies
uv sync

# Verify installation
uv run weekly-summary --help
```

## Configuration

### Using Mock Data (Recommended for Testing)

Use the provided `config.mock.yaml` - no API tokens required:

```yaml
sources:
  github_mock:
    enabled: true
    username: "demo_developer"

  slack_mock:
    enabled: true

  email_mock:
    enabled: true
    email: "developer@acme-corp.com"
```

### Using Real APIs

1. Copy the example configuration:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Configure your API credentials in `config.yaml`:

   **GitHub**:
   - Create a [personal access token](https://github.com/settings/tokens)
   - Requires `repo` scope for private repos, `public_repo` for public only

   **Slack**:
   - Create a [user token](https://api.slack.com/authentication/token-types#user) (starts with `xoxp-`)
   - Requires `channels:history`, `users:read`, `im:history` scopes

   **Email**:
   - Use IMAP credentials (for Gmail, create an [app password](https://support.google.com/accounts/answer/185833))
   - Configure host, port, and credentials

### AI-Powered Summaries

The tool can automatically generate summaries of your work using Claude AI:

**With Mock Data (Testing)**:
- Summaries are automatically generated with mock data
- No API key required

**With Real Data**:
- Set the `ANTHROPIC_API_KEY` environment variable
- Get an API key from [Anthropic Console](https://console.anthropic.com/)
- Summaries will automatically be added to the top of reports

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
uv run weekly-summary --config config.yaml
```

### Filtering Sources

Reduce noise by targeting specific repos and channels:

**GitHub - Filter by Repository**:
```yaml
github:
  enabled: true
  token: "ghp_..."
  username: "your_username"
  repos:
    - "your-org/backend"
    - "your-org/frontend"
```

**Slack - Filter by Channel**:
```yaml
slack:
  enabled: true
  token: "xoxp-..."
  channels:
    - "C01ABC123"  # engineering channel ID
    - "C02DEF456"  # backend-team channel ID
```

## Usage

### Quick Start with Website

The easiest way to see your weekly summaries is through the web interface:

```bash
# Generate mock data, build website, and start server (all-in-one)
make website

# Visit http://localhost:1313 to view your weekly summaries
```

This command will:
1. Generate a report with mock data
2. Build the Hugo website
3. Start a local development server

### Makefile Commands

```bash
make help           # Show all available commands
make generate-mock  # Generate report with mock data
make generate       # Generate report with real APIs
make build          # Build Hugo website
make serve          # Start Hugo development server
make website        # All-in-one: generate + build + serve
make test           # Run tests
make clean          # Remove generated files
```

### Basic Usage

```bash
# Generate report for last week (Monday-Sunday) with mock data
uv run weekly-summary --config config.mock.yaml

# Generate report for specific date range
uv run weekly-summary --config config.mock.yaml \
  --start-date 2024-01-01 \
  --end-date 2024-01-07

# Use real APIs
uv run weekly-summary --config config.yaml

# Custom output directory
uv run weekly-summary --config config.mock.yaml --output-dir my-reports
```

### CLI Options

- `--config, -c`: Path to configuration file (default: `config.yaml`)
- `--start-date, -s`: Start date in YYYY-MM-DD format (default: last Monday)
- `--end-date, -e`: End date in YYYY-MM-DD format (default: last Sunday)
- `--output, -o`: Custom output filename
- `--output-dir, -d`: Output directory for reports (default: `reports`)

## Report Format

Reports are generated as markdown files with:

- **Summary Section**: Total activities and breakdown by source
- **Activities by Source**: Grouped by source (GitHub, Slack, Email) and activity type
- **Timeline View**: Chronological view of all activities by day

Example output:
```
reports/
 weekly-summary_2024-01-01_to_2024-01-07.md
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_mock_connectors.py

# Run with coverage
uv run pytest --cov=src
```

### Code Quality

```bash
# Lint code
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check --fix src tests

# Format code
uv run black src tests
```

## Architecture

The project uses a plugin architecture for easy extensibility:

- **BaseConnector**: Abstract base class for all data sources
- **Connectors**: Individual implementations for GitHub, Slack, Email, and mocks
- **ReportGenerator**: Aggregates and formats activities into markdown
- **CLI**: Orchestrates configuration, fetching, and report generation

### Adding a New Connector

1. Create a new class extending `BaseConnector` in `src/weekly_summary/connectors/`
2. Implement required methods: `fetch_activities()`, `validate_config()`, `name`
3. Register in `CONNECTOR_CLASSES` in `cli.py`
4. Add configuration example to `config.example.yaml`
5. Write tests in `tests/`

See `src/weekly_summary/connectors/mock.py` for a simple example.

## Building a Website with Hugo

The project includes a complete Hugo website setup for browsing your weekly summaries:

### Features

- **Clean, Responsive Design**: Mobile-friendly interface for viewing reports
- **Automatic Front Matter**: Reports include Hugo metadata (date, activity counts, source breakdown)
- **List and Detail Views**: Homepage shows all reports, click to view full details
- **Statistics Dashboard**: Visual breakdown of activities by source
- **Easy Navigation**: Timeline-based organization with clear date ranges

### Structure

- `site/`: Hugo site configuration and theme
- `site/themes/weekly-summary/`: Custom theme optimized for weekly summaries
- `reports/`: Markdown reports (used as Hugo content via `contentDir`)

### Usage

```bash
# One command to generate and view
make website

# Or step by step
make generate-mock  # Generate reports with mock data
make build          # Build Hugo site
make serve          # Start local server at http://localhost:1313

# For production deployment
cd site && hugo     # Generates static site in site/public/
```

### Customization

To customize the website:
- Edit `site/hugo.toml` for site configuration
- Modify templates in `site/themes/weekly-summary/layouts/`
- Update styles in `site/themes/weekly-summary/static/css/style.css`

## License

[Add your license here]

## Contributing

Contributions are welcome! Please ensure all tests pass and add tests for new features.
