"""Base connector interface for all data sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Activity:
    """Represents a single activity from any data source."""

    timestamp: datetime
    title: str
    description: str
    source: str  # e.g., "github", "slack", "email"
    activity_type: str  # e.g., "pr_review", "commit", "message", "email"
    url: str | None = None
    metadata: dict[str, Any] | None = None

    def __lt__(self, other: "Activity") -> bool:
        """Enable sorting by timestamp."""
        return self.timestamp < other.timestamp


class BaseConnector(ABC):
    """Abstract base class for all connectors."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the connector with configuration.

        Args:
            config: Configuration dictionary specific to this connector
        """
        self.config = config

    @abstractmethod
    def fetch_activities(self, start_date: datetime, end_date: datetime) -> list[Activity]:
        """
        Fetch activities from the data source within the specified date range.

        Args:
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)

        Returns:
            List of Activity objects
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the connector is properly configured.

        Returns:
            True if configuration is valid, raises exception otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this connector."""
        pass
