"""Slack connector for fetching messages and activity."""

from datetime import datetime
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .base import Activity, BaseConnector


class SlackConnector(BaseConnector):
    """Connector for Slack activities."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Slack connector.

        Expected config:
            - token: Slack user token (starts with xoxp-)
            - channels: Optional list of channel IDs to monitor
        """
        super().__init__(config)
        self.token = config.get("token")
        self.channels = config.get("channels", [])
        self.client: WebClient | None = None
        self.user_id: str | None = None

    @property
    def name(self) -> str:
        return "slack"

    def validate_config(self) -> bool:
        """Validate Slack configuration."""
        if not self.token:
            raise ValueError("Slack token is required")

        try:
            self.client = WebClient(token=self.token)
            # Test authentication and get user ID
            response = self.client.auth_test()
            self.user_id = response["user_id"]
            return True
        except SlackApiError as e:
            raise ValueError(f"Invalid Slack token: {e}")

    def fetch_activities(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch Slack activities within the date range."""
        if not self.client:
            self.validate_config()

        activities = []

        # Get channels to search
        channels = self._get_channels()

        # Fetch messages from each channel
        for channel in channels:
            activities.extend(
                self._fetch_messages_from_channel(channel, start_date, end_date)
            )

        return sorted(activities)

    def _get_channels(self) -> list[dict[str, Any]]:
        """Get list of channels to monitor."""
        # Ensure client is initialized
        if self.client is None:
            return []

        if self.channels:
            # Get specific channels
            channels: list[dict[str, Any]] = []
            for channel_id in self.channels:
                try:
                    response = self.client.conversations_info(channel=channel_id)
                    channel = response.get("channel")
                    if channel is not None:
                        channels.append(channel)
                except SlackApiError:
                    continue
            return channels

        # Get all public channels and private channels the user is in
        all_channels: list[dict[str, Any]] = []
        try:
            # Public channels
            response = self.client.conversations_list(
                types="public_channel,private_channel"
            )
            all_channels.extend(response.get("channels", []))

            # Direct messages
            response = self.client.conversations_list(types="im")
            all_channels.extend(response.get("channels", []))
        except SlackApiError:
            pass

        return all_channels

    def _fetch_messages_from_channel(
        self, channel: dict[str, Any], start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch messages from a specific channel."""
        activities: list[Activity] = []
        channel_id = channel["id"]
        channel_name = channel.get("name", channel_id)

        # Ensure client is initialized
        if self.client is None:
            return activities

        try:
            # Convert datetime to Unix timestamp
            oldest = str(int(start_date.timestamp()))
            latest = str(int(end_date.timestamp()))

            response = self.client.conversations_history(
                channel=channel_id, oldest=oldest, latest=latest, limit=1000
            )

            messages = response.get("messages", [])

            for message in messages:
                # Only include messages sent by the user
                if message.get("user") != self.user_id:
                    continue

                timestamp = datetime.fromtimestamp(float(message["ts"]))

                # Get thread context if message is a reply
                thread_context = ""
                if "thread_ts" in message and message["thread_ts"] != message["ts"]:
                    thread_context = " (thread reply)"

                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=f"Message in #{channel_name}{thread_context}",
                        description=message.get("text", "")[
                            :200
                        ],  # Truncate long messages
                        source=self.name,
                        activity_type="message",
                        url=self._get_message_url(channel_id, message["ts"]),
                        metadata={
                            "channel": channel_name,
                            "channel_id": channel_id,
                            "is_thread": "thread_ts" in message,
                        },
                    )
                )

        except SlackApiError:
            pass

        return activities

    def _get_message_url(self, channel_id: str, ts: str) -> str:
        """Generate Slack message URL."""
        # Ensure client is initialized
        if self.client is None:
            return ""

        # Get workspace domain
        try:
            response = self.client.team_info()
            team = response.get("team")
            if team is None:
                return ""
            team_domain = team.get("domain", "")
            message_id = ts.replace(".", "")
            return (
                f"https://{team_domain}.slack.com/archives/{channel_id}/p{message_id}"
            )
        except SlackApiError:
            return ""
