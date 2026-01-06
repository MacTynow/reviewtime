"""Weekly Summary Generator - Aggregate work activities from GitHub, Slack, and Email."""

__version__ = "0.1.0"

from .connectors.base import Activity, BaseConnector
from .connectors.email import EmailConnector
from .connectors.github import GitHubConnector
from .connectors.slack import SlackConnector
from .connectors.mock import MockEmailConnector, MockGitHubConnector, MockSlackConnector
from .report.generator import ReportGenerator

__all__ = [
    "Activity",
    "BaseConnector",
    "EmailConnector",
    "GitHubConnector",
    "SlackConnector",
    "MockEmailConnector",
    "MockGitHubConnector",
    "MockSlackConnector",
    "ReportGenerator",
]
