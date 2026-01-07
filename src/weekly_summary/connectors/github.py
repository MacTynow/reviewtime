"""GitHub connector for fetching PRs, reviews, and commits."""

from datetime import datetime
from typing import Any

from github import Auth, Github
from github.GithubException import BadCredentialsException, GithubException

from .base import Activity, BaseConnector


class GitHubConnector(BaseConnector):
    """Connector for GitHub activities."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize GitHub connector.

        Expected config:
            - token: GitHub personal access token
            - username: GitHub username to track activities for
            - repos: Optional list of repo names to filter (format: "owner/repo")
        """
        super().__init__(config)
        self.token = config.get("token")
        self.username = config.get("username")
        self.repos = config.get("repos", [])
        self.client: Github | None = None

    @property
    def name(self) -> str:
        return "github"

    def validate_config(self) -> bool:
        """Validate GitHub configuration."""
        if not self.token:
            raise ValueError("GitHub token is required")
        if not self.username:
            raise ValueError("GitHub username is required")

        try:
            auth = Auth.Token(self.token)
            self.client = Github(auth=auth)
            # Test authentication
            self.client.get_user().login
            return True
        except BadCredentialsException as e:
            raise ValueError(f"Invalid GitHub token: {e}")
        except GithubException as e:
            raise ValueError(f"GitHub API error: {e}")

    def fetch_activities(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch GitHub activities within the date range."""
        if not self.client:
            self.validate_config()

        activities = []

        # Fetch commits
        activities.extend(self._fetch_commits(start_date, end_date))

        # Fetch PRs created
        activities.extend(self._fetch_prs_created(start_date, end_date))

        # Fetch PR reviews
        activities.extend(self._fetch_pr_reviews(start_date, end_date))

        return sorted(activities)

    def _fetch_commits(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch commits by the user."""
        activities = []

        # Ensure client is initialized
        if self.client is None:
            return activities

        if self.repos:
            repos = [self.client.get_repo(repo) for repo in self.repos]
        else:
            # Get all repos the user has access to
            user = self.client.get_user()
            repos = list(user.get_repos())

        for repo in repos:
            try:
                # username is validated in validate_config, so it's not None here
                commits = repo.get_commits(
                    author=self.username or "", since=start_date, until=end_date
                )
                for commit in commits:
                    if (
                        commit.commit.author.date >= start_date
                        and commit.commit.author.date <= end_date
                    ):
                        activities.append(
                            Activity(
                                timestamp=commit.commit.author.date,
                                title=f"Commit to {repo.full_name}",
                                description=commit.commit.message.split("\n")[0],
                                source=self.name,
                                activity_type="commit",
                                url=commit.html_url,
                                metadata={
                                    "repo": repo.full_name,
                                    "sha": commit.sha,
                                    "additions": (
                                        commit.stats.additions if commit.stats else 0
                                    ),
                                    "deletions": (
                                        commit.stats.deletions if commit.stats else 0
                                    ),
                                },
                            )
                        )
            except GithubException:
                # Skip repos we don't have access to
                continue

        return activities

    def _fetch_prs_created(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch PRs created by the user."""
        activities = []

        # Ensure client is initialized
        if self.client is None:
            return activities

        # Search for PRs created by the user
        query = f"author:{self.username} is:pr created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        if self.repos:
            repo_query = " ".join([f"repo:{repo}" for repo in self.repos])
            query = f"{query} {repo_query}"

        try:
            issues = self.client.search_issues(query)
            for issue in issues:
                if issue.created_at >= start_date and issue.created_at <= end_date:
                    pr = issue.as_pull_request()
                    activities.append(
                        Activity(
                            timestamp=issue.created_at,
                            title=f"Created PR: {issue.title}",
                            description=issue.body or "",
                            source=self.name,
                            activity_type="pr_created",
                            url=issue.html_url,
                            metadata={
                                "repo": issue.repository.full_name,
                                "number": issue.number,
                                "state": issue.state,
                                "merged": pr.merged if pr else False,
                            },
                        )
                    )
        except GithubException:
            pass

        return activities

    def _fetch_pr_reviews(
        self, start_date: datetime, end_date: datetime
    ) -> list[Activity]:
        """Fetch PR reviews by the user."""
        activities = []

        # Ensure client is initialized
        if self.client is None:
            return activities

        # Search for PRs where the user was requested as a reviewer or reviewed
        query = f"reviewed-by:{self.username} is:pr updated:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
        if self.repos:
            repo_query = " ".join([f"repo:{repo}" for repo in self.repos])
            query = f"{query} {repo_query}"

        try:
            issues = self.client.search_issues(query)
            for issue in issues:
                pr = issue.as_pull_request()
                reviews = pr.get_reviews()

                for review in reviews:
                    if (
                        review.user.login == self.username
                        and review.submitted_at
                        and review.submitted_at >= start_date
                        and review.submitted_at <= end_date
                    ):
                        activities.append(
                            Activity(
                                timestamp=review.submitted_at,
                                title=f"Reviewed PR: {issue.title}",
                                description=review.body or f"{review.state} review",
                                source=self.name,
                                activity_type="pr_review",
                                url=issue.html_url,
                                metadata={
                                    "repo": issue.repository.full_name,
                                    "number": issue.number,
                                    "review_state": review.state,
                                },
                            )
                        )
        except GithubException:
            pass

        return activities
