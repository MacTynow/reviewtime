"""Mock connectors for testing and development with realistic data."""

from datetime import datetime, timedelta
from typing import Any

from .base import Activity, BaseConnector


class MockGitHubConnector(BaseConnector):
    """Mock GitHub connector with fake data and repo filtering."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.username = config.get("username", "mock_user")
        self.repos = config.get("repos", [])  # Optional repo filter

    def validate_config(self) -> bool:
        """Mock validation always succeeds."""
        return True

    @property
    def name(self) -> str:
        return "github_mock"

    def fetch_activities(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Generate fake GitHub activities with optional repo filtering."""
        activities = []

        # Generate commits spread across the week
        commit_data = [
            {
                "title": "Fix authentication bug in login flow",
                "description": "Fixed issue where users couldn't log in with special characters in password",
                "repo": "acme-corp/backend",
                "sha": "a1b2c3d",
                "additions": 45,
                "deletions": 12,
                "days_ago": 1,
            },
            {
                "title": "Add user profile caching",
                "description": "Implemented Redis caching for user profiles to improve performance",
                "repo": "acme-corp/backend",
                "sha": "e4f5g6h",
                "additions": 234,
                "deletions": 18,
                "days_ago": 2,
            },
            {
                "title": "Update dependencies to latest versions",
                "description": "Bumped all npm packages to latest stable versions",
                "repo": "acme-corp/frontend",
                "sha": "i7j8k9l",
                "additions": 15,
                "deletions": 15,
                "days_ago": 3,
            },
            {
                "title": "Refactor database connection pool",
                "description": "Improved connection pool management and error handling",
                "repo": "acme-corp/backend",
                "sha": "m0n1o2p",
                "additions": 156,
                "deletions": 89,
                "days_ago": 4,
            },
            {
                "title": "Add unit tests for user service",
                "description": "Added comprehensive unit tests covering edge cases",
                "repo": "acme-corp/backend",
                "sha": "q3r4s5t",
                "additions": 312,
                "deletions": 5,
                "days_ago": 5,
            },
            {
                "title": "Fix memory leak in websocket handler",
                "description": "Properly cleanup websocket connections to prevent memory leaks",
                "repo": "acme-corp/backend",
                "sha": "u6v7w8x",
                "additions": 67,
                "deletions": 23,
                "days_ago": 2,
            },
            {
                "title": "Improve error messages in API",
                "description": "Made error messages more user-friendly and actionable",
                "repo": "acme-corp/backend",
                "sha": "y9z0a1b",
                "additions": 89,
                "deletions": 34,
                "days_ago": 3,
            },
        ]

        for commit in commit_data:
            # Apply repo filter if specified
            if self.repos and commit["repo"] not in self.repos:
                continue

            timestamp = end_date - timedelta(days=commit["days_ago"], hours=10)
            if start_date <= timestamp <= end_date:
                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=commit["title"],
                        description=commit["description"],
                        source="github",
                        activity_type="commit",
                        url=f"https://github.com/{commit['repo']}/commit/{commit['sha']}",
                        metadata={
                            "repo": commit["repo"],
                            "sha": commit["sha"],
                            "additions": commit["additions"],
                            "deletions": commit["deletions"],
                        },
                    )
                )

        # Generate PRs
        pr_data = [
            {
                "title": "Feature: Add email notification system",
                "description": "Implemented email notifications for important user events",
                "repo": "acme-corp/backend",
                "number": 142,
                "merged": True,
                "days_ago": 2,
            },
            {
                "title": "Refactor: Improve API response format",
                "description": "Standardized API responses across all endpoints",
                "repo": "acme-corp/backend",
                "number": 145,
                "merged": False,
                "days_ago": 1,
            },
            {
                "title": "Feature: Dark mode support",
                "description": "Added dark mode theme with user preference persistence",
                "repo": "acme-corp/frontend",
                "number": 78,
                "merged": True,
                "days_ago": 4,
            },
        ]

        for pr in pr_data:
            if self.repos and pr["repo"] not in self.repos:
                continue

            timestamp = end_date - timedelta(days=pr["days_ago"], hours=14)
            if start_date <= timestamp <= end_date:
                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=pr["title"],
                        description=pr["description"],
                        source="github",
                        activity_type="pr_created",
                        url=f"https://github.com/{pr['repo']}/pull/{pr['number']}",
                        metadata={
                            "repo": pr["repo"],
                            "number": pr["number"],
                            "merged": pr["merged"],
                        },
                    )
                )

        # Generate PR reviews
        review_data = [
            {
                "title": "Reviewed: Add metrics dashboard",
                "description": "Reviewed and approved metrics dashboard implementation",
                "repo": "acme-corp/frontend",
                "number": 89,
                "state": "APPROVED",
                "days_ago": 3,
            },
            {
                "title": "Reviewed: Update deployment scripts",
                "description": "Requested changes to improve error handling",
                "repo": "acme-corp/devops",
                "number": 23,
                "state": "CHANGES_REQUESTED",
                "days_ago": 4,
            },
        ]

        for review in review_data:
            if self.repos and review["repo"] not in self.repos:
                continue

            timestamp = end_date - timedelta(days=review["days_ago"], hours=15)
            if start_date <= timestamp <= end_date:
                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=review["title"],
                        description=review["description"],
                        source="github",
                        activity_type="pr_review",
                        url=f"https://github.com/{review['repo']}/pull/{review['number']}",
                        metadata={
                            "repo": review["repo"],
                            "number": review["number"],
                            "state": review["state"],
                        },
                    )
                )

        return activities


class MockSlackConnector(BaseConnector):
    """Mock Slack connector with realistic chatter and channel filtering."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.channels = config.get("channels", [])  # Optional channel filter

    def validate_config(self) -> bool:
        """Mock validation always succeeds."""
        return True

    @property
    def name(self) -> str:
        return "slack_mock"

    def fetch_activities(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Generate fake Slack activities with realistic chatter and channel filtering."""
        activities = []

        # Much more realistic Slack messages with varied content
        message_data = [
            # Engineering channel - technical discussions
            {
                "title": "Shared weekly sprint progress in #engineering",
                "description": "Updated team on completion of authentication feature and upcoming work",
                "channel": "engineering",
                "channel_id": "C01ABC123",
                "is_thread": False,
                "days_ago": 1,
                "hours": 9,
            },
            {
                "title": "Question about database migration strategy in #engineering",
                "description": "Asked team for input on zero-downtime migration approach",
                "channel": "engineering",
                "channel_id": "C01ABC123",
                "is_thread": False,
                "days_ago": 2,
                "hours": 10,
            },
            {
                "title": "Shared performance optimization results in #engineering",
                "description": "Posted benchmarks showing 40% improvement in API response times",
                "channel": "engineering",
                "channel_id": "C01ABC123",
                "is_thread": False,
                "days_ago": 4,
                "hours": 15,
            },
            # Backend team - specific technical work
            {
                "title": "Discussed architecture decisions in #backend-team",
                "description": "Proposed new microservices architecture for payment processing",
                "channel": "backend-team",
                "channel_id": "C02DEF456",
                "is_thread": False,
                "days_ago": 2,
                "hours": 14,
            },
            {
                "title": "Shared API design document in #backend-team",
                "description": "Posted draft of new REST API design for team review",
                "channel": "backend-team",
                "channel_id": "C02DEF456",
                "is_thread": False,
                "days_ago": 3,
                "hours": 11,
            },
            {
                "title": "Discussed caching strategy in #backend-team",
                "description": "Debated Redis vs Memcached for session storage",
                "channel": "backend-team",
                "channel_id": "C02DEF456",
                "is_thread": False,
                "days_ago": 4,
                "hours": 16,
            },
            # DevOps - deployment and infrastructure
            {
                "title": "Responded to deployment question in thread in #devops",
                "description": "Helped troubleshoot production deployment issue",
                "channel": "devops",
                "channel_id": "C03GHI789",
                "is_thread": True,
                "days_ago": 2,
                "hours": 16,
            },
            {
                "title": "Announced successful migration in #devops",
                "description": "Database migration completed with zero downtime",
                "channel": "devops",
                "channel_id": "C03GHI789",
                "is_thread": False,
                "days_ago": 3,
                "hours": 18,
            },
            {
                "title": "Discussed monitoring alerts in #devops",
                "description": "Proposed new alerting thresholds for CPU usage",
                "channel": "devops",
                "channel_id": "C03GHI789",
                "is_thread": False,
                "days_ago": 5,
                "hours": 14,
            },
            # Code review discussions
            {
                "title": "Code review feedback in #pull-requests",
                "description": "Provided detailed feedback on database migration PR",
                "channel": "pull-requests",
                "channel_id": "C04JKL012",
                "is_thread": False,
                "days_ago": 3,
                "hours": 11,
            },
            {
                "title": "Requested review in #pull-requests",
                "description": "Asked for eyes on authentication refactor PR",
                "channel": "pull-requests",
                "channel_id": "C04JKL012",
                "is_thread": False,
                "days_ago": 1,
                "hours": 15,
            },
            # Product discussions
            {
                "title": "Meeting notes shared in #product-sync",
                "description": "Documented key decisions from product planning meeting",
                "channel": "product-sync",
                "channel_id": "C05MNO345",
                "is_thread": False,
                "days_ago": 5,
                "hours": 13,
            },
            {
                "title": "Feedback on new feature proposal in #product-sync",
                "description": "Provided technical feasibility assessment for Q2 roadmap items",
                "channel": "product-sync",
                "channel_id": "C05MNO345",
                "is_thread": False,
                "days_ago": 3,
                "hours": 10,
            },
            # Random/General chatter
            {
                "title": "Shared article about microservices in #random",
                "description": "Posted interesting read on service mesh patterns",
                "channel": "random",
                "channel_id": "C06PQR678",
                "is_thread": False,
                "days_ago": 4,
                "hours": 12,
            },
            {
                "title": "Lunch plans coordination in #random",
                "description": "Organized team lunch for Friday",
                "channel": "random",
                "channel_id": "C06PQR678",
                "is_thread": False,
                "days_ago": 2,
                "hours": 11,
            },
            {
                "title": "Coffee chat follow-up in #random",
                "description": "Thanks for the coffee chat! Great discussion about career growth",
                "channel": "random",
                "channel_id": "C06PQR678",
                "is_thread": False,
                "days_ago": 1,
                "hours": 16,
            },
            # Incident response
            {
                "title": "Production incident alert in #incidents",
                "description": "API response times spiking, investigating root cause",
                "channel": "incidents",
                "channel_id": "C07STU901",
                "is_thread": False,
                "days_ago": 3,
                "hours": 14,
            },
            {
                "title": "Incident resolution update in #incidents",
                "description": "Issue resolved - database connection pool exhaustion. Applied fix and monitoring",
                "channel": "incidents",
                "channel_id": "C07STU901",
                "is_thread": True,
                "days_ago": 3,
                "hours": 15,
            },
            # Security discussions
            {
                "title": "Security review feedback in #security",
                "description": "Addressed concerns about API authentication flow",
                "channel": "security",
                "channel_id": "C08VWX234",
                "is_thread": False,
                "days_ago": 4,
                "hours": 13,
            },
            # Status updates
            {
                "title": "Daily standup update in #standup",
                "description": "Yesterday: Fixed auth bug. Today: Working on caching layer. Blockers: None",
                "channel": "standup",
                "channel_id": "C09YZA567",
                "is_thread": False,
                "days_ago": 1,
                "hours": 9,
            },
            {
                "title": "Daily standup update in #standup",
                "description": "Yesterday: Caching layer. Today: Performance testing. Blockers: Waiting on staging env",
                "channel": "standup",
                "channel_id": "C09YZA567",
                "is_thread": False,
                "days_ago": 2,
                "hours": 9,
            },
            {
                "title": "Daily standup update in #standup",
                "description": "Yesterday: Performance tests. Today: Code review and documentation. Blockers: None",
                "channel": "standup",
                "channel_id": "C09YZA567",
                "is_thread": False,
                "days_ago": 3,
                "hours": 9,
            },
        ]

        for msg in message_data:
            # Apply channel filter if specified
            if self.channels and msg["channel_id"] not in self.channels:
                continue

            timestamp = end_date - timedelta(
                days=msg["days_ago"], hours=24 - msg["hours"]
            )
            if start_date <= timestamp <= end_date:
                ts = f"{int(timestamp.timestamp())}.000000"
                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=msg["title"],
                        description=msg["description"],
                        source="slack",
                        activity_type="message",
                        url=f"https://acme-corp.slack.com/archives/{msg['channel_id']}/p{ts.replace('.', '')}",
                        metadata={
                            "channel": msg["channel"],
                            "channel_id": msg["channel_id"],
                            "is_thread": msg["is_thread"],
                        },
                    )
                )

        return activities


class MockEmailConnector(BaseConnector):
    """Mock Email connector with fake data."""

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.email = config.get("email", "user@example.com")

    def validate_config(self) -> bool:
        """Mock validation always succeeds."""
        return True

    @property
    def name(self) -> str:
        return "email_mock"

    def fetch_activities(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Generate fake email activities."""
        activities = []

        email_data = [
            {
                "type": "sent",
                "title": "Q1 Project Status Update",
                "description": "Sent quarterly update to stakeholders",
                "to": ["stakeholders@acme-corp.com"],
                "cc": ["team@acme-corp.com"],
                "subject": "Q1 Project Status Update - Backend Team",
                "has_attachments": True,
                "days_ago": 1,
                "hours": 10,
            },
            {
                "type": "sent",
                "title": "Re: Database migration plan",
                "description": "Responded with detailed migration strategy",
                "to": ["dba@acme-corp.com"],
                "cc": [],
                "subject": "Re: Database migration plan",
                "has_attachments": False,
                "days_ago": 2,
                "hours": 11,
            },
            {
                "type": "received",
                "title": "Security audit requirements",
                "description": "Received security audit checklist from InfoSec",
                "from": "security@acme-corp.com",
                "to": [self.email],
                "cc": ["engineering@acme-corp.com"],
                "subject": "Security audit requirements for Q1",
                "has_attachments": True,
                "days_ago": 2,
                "hours": 14,
            },
            {
                "type": "sent",
                "title": "API documentation updates",
                "description": "Shared updated API documentation with external partners",
                "to": ["partners@external-company.com"],
                "cc": ["product@acme-corp.com"],
                "subject": "API Documentation v2.1 - Breaking Changes",
                "has_attachments": True,
                "days_ago": 3,
                "hours": 15,
            },
            {
                "type": "received",
                "title": "Interview feedback request",
                "description": "HR requested feedback on recent engineering candidate",
                "from": "hr@acme-corp.com",
                "to": [self.email],
                "cc": [],
                "subject": "Interview Feedback - Senior Backend Engineer",
                "has_attachments": False,
                "days_ago": 4,
                "hours": 9,
            },
            {
                "type": "sent",
                "title": "Performance optimization proposal",
                "description": "Sent proposal for database optimization initiative",
                "to": ["engineering-leads@acme-corp.com"],
                "cc": ["cto@acme-corp.com"],
                "subject": "Proposal: Database Performance Optimization Initiative",
                "has_attachments": True,
                "days_ago": 5,
                "hours": 16,
            },
        ]

        for email in email_data:
            timestamp = end_date - timedelta(
                days=email["days_ago"], hours=24 - email["hours"]
            )
            if start_date <= timestamp <= end_date:
                metadata = {
                    "folder": "Sent" if email["type"] == "sent" else "INBOX",
                    "to": email["to"],
                    "cc": email["cc"],
                    "subject": email["subject"],
                    "has_attachments": email["has_attachments"],
                }

                if email["type"] == "sent":
                    metadata["from"] = self.email
                else:
                    metadata["from"] = email["from"]

                activities.append(
                    Activity(
                        timestamp=timestamp,
                        title=email["title"],
                        description=email["description"],
                        source="email",
                        activity_type=f"email_{email['type']}",
                        url=None,
                        metadata=metadata,
                    )
                )

        return activities
