"""Email connector for fetching emails via IMAP."""

from datetime import datetime
from typing import Any

from imap_tools.query import AND
from imap_tools.mailbox import MailBox, MailBoxUnencrypted
from imap_tools.message import MailMessage

from .base import Activity, BaseConnector


class EmailConnector(BaseConnector):
    """Connector for email activities via IMAP."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Email connector.

        Expected config:
            - host: IMAP server host (e.g., imap.gmail.com)
            - email: Email address
            - password: App-specific password or IMAP password
            - port: IMAP port (default: 993 for SSL)
            - use_ssl: Whether to use SSL (default: True)
            - folders: Optional list of folder names to monitor (default: ["INBOX", "Sent"])
        """
        super().__init__(config)
        self.host = config.get("host")
        self.email = config.get("email")
        self.password = config.get("password")
        self.port = config.get("port", 993)
        self.use_ssl = config.get("use_ssl", True)
        self.folders = config.get("folders", ["INBOX", "Sent"])

    @property
    def name(self) -> str:
        return "email"

    def validate_config(self) -> bool:
        """Validate email configuration."""
        if not self.host:
            raise ValueError("IMAP host is required")
        if not self.email:
            raise ValueError("Email address is required")
        if not self.password:
            raise ValueError("Email password is required")

        # Test connection
        try:
            mailbox_class = MailBox if self.use_ssl else MailBoxUnencrypted
            with mailbox_class(self.host, port=self.port).login(self.email, self.password):
                return True
        except Exception as e:
            raise ValueError(f"Failed to connect to IMAP server: {e}")

    def fetch_activities(self, start_date: datetime, end_date: datetime) -> list[Activity]:
        """Fetch email activities within the date range."""
        activities = []

        mailbox_class = MailBox if self.use_ssl else MailBoxUnencrypted

        with mailbox_class(self.host, port=self.port).login(self.email, self.password) as mailbox:
            for folder in self.folders:
                try:
                    mailbox.folder.set(folder)
                    activities.extend(self._fetch_emails_from_folder(mailbox, folder, start_date, end_date))
                except Exception:
                    # Skip folders we can't access
                    continue

        return sorted(activities)

    def _fetch_emails_from_folder(
        self, mailbox: MailBox, folder: str, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch emails from a specific folder."""
        activities = []

        # Search for emails in date range
        # For sent folder, we want emails from the user
        # For inbox, we want emails to the user
        criteria = AND(date_gte=start_date.date(), date_lte=end_date.date())

        try:
            for msg in mailbox.fetch(criteria):
                activities.append(self._convert_message_to_activity(msg, folder))
        except Exception:
            pass

        return activities

    def _convert_message_to_activity(self, msg: MailMessage, folder: str) -> Activity:
        """Convert email message to Activity."""
        # Determine if this is sent or received
        is_sent = folder.lower() in ["sent", "sent items", "sent mail"]

        if is_sent:
            title = f"Sent email to {', '.join(msg.to_values)}"
            activity_type = "email_sent"
        else:
            title = f"Received email from {msg.from_}"
            activity_type = "email_received"

        # Get plain text or HTML preview
        description = msg.text or msg.html[:200] if msg.html else ""
        if len(description) > 200:
            description = description[:200] + "..."

        # Use the message date (when it was sent/received)
        timestamp = msg.date

        return Activity(
            timestamp=timestamp,
            title=f"{title}: {msg.subject}",
            description=description,
            source=self.name,
            activity_type=activity_type,
            url=None,  # Email doesn't have URLs
            metadata={
                "folder": folder,
                "from": msg.from_,
                "to": msg.to_values,
                "cc": msg.cc_values,
                "subject": msg.subject,
                "has_attachments": len(msg.attachments) > 0,
            },
        )
