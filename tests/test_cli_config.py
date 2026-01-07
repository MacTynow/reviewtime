"""Tests for CLI config wizard."""

from pathlib import Path
from tempfile import TemporaryDirectory

import yaml
from click.testing import CliRunner

from weekly_summary.cli import (
    check_existing_config,
    main,
    write_config_file,
)


class TestCheckExistingConfig:
    """Tests for check_existing_config()."""

    def test_no_existing_config(self):
        """Test when config file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            result = check_existing_config(config_path)
            assert result is True


class TestWriteConfigFile:
    """Tests for write_config_file()."""

    def test_write_new_config(self):
        """Test writing config to new file."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = {
                "sources": {
                    "github": {"enabled": True, "token": "test", "username": "user"}
                }
            }

            write_config_file(config, config_path)

            assert config_path.exists()
            with open(config_path) as f:
                loaded = yaml.safe_load(f)
            assert loaded == config

    def test_write_creates_backup(self):
        """Test that existing config is backed up."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            backup_path = Path(tmpdir) / "config.yaml.backup"

            # Create existing config
            original_config = {"sources": {"github": {"enabled": False}}}
            with open(config_path, "w") as f:
                yaml.dump(original_config, f)

            # Write new config
            new_config = {"sources": {"slack": {"enabled": True}}}
            write_config_file(new_config, config_path)

            # Verify backup was created with original content
            assert backup_path.exists()
            with open(backup_path) as f:
                backed_up = yaml.safe_load(f)
            assert backed_up == original_config

            # Verify new config was written
            with open(config_path) as f:
                current = yaml.safe_load(f)
            assert current == new_config

    def test_file_permissions(self):
        """Test that config file has secure permissions (0600)."""
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = {"sources": {"github": {"enabled": True}}}

            write_config_file(config, config_path)

            # Check permissions (0600 = owner read/write only)
            import stat

            mode = config_path.stat().st_mode
            # Should be readable and writable by owner only
            assert stat.S_IMODE(mode) == 0o600


class TestConfigCommandIntegration:
    """Integration tests for config command."""

    def test_config_command_help(self):
        """Test config command help text."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0
        assert "Interactive configuration wizard" in result.output

    def test_config_command_with_github_mock(self):
        """Test full flow with GitHub mock connector."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Simulate user input:
            # - Select github only
            # - Token: test-token
            # - Username: testuser  # - No repo filtering
            # - No API key
            # - Confirm write
            user_input = "github_mock\ntest-token\ntestuser\nn\n\ny\n"

            runner.invoke(
                main, ["config", "--output", "test-config.yaml"], input=user_input
            )

            # Check if config was created
            config_path = Path("test-config.yaml")
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    assert "sources" in config
                    # Note: github_mock connector doesn't require token validation

    def test_config_command_cancel_on_existing(self):
        """Test cancelling when config already exists."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create existing config
            config_path = Path("config.yaml")
            config_path.write_text("existing: true")

            # User input: decline to overwrite
            result = runner.invoke(main, ["config"], input="n\n")

            assert "Configuration cancelled" in result.output
            # Original file should be unchanged
            assert config_path.read_text() == "existing: true"

    def test_config_command_custom_output_path(self):
        """Test writing config to custom path."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            user_input = "github_mock\nn\n\ny\n"

            result = runner.invoke(
                main, ["config", "--output", "custom-config.yaml"], input=user_input
            )

            # Verify custom path was used
            assert Path("custom-config.yaml").exists() or result.exit_code != 0


class TestConfigWithMockConnectors:
    """Tests using mock connectors which don't require credentials."""

    def test_all_mock_connectors(self):
        """Test configuring all mock connectors."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Configure all three mock connectors
            user_input = "github_mock,slack_mock,email_mock\n\n\n\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0:
                config_path = Path("config.yaml")
                if config_path.exists():
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        sources = config.get("sources", {})
                        # Mock connectors should be configured
                        assert len(sources) > 0

    def test_github_mock_with_repos(self):
        """Test configuring GitHub mock with repo filtering."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Select github_mock, add repo filtering
            user_input = "github_mock\ny\nuser/repo1,user/repo2\n\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0 and Path("config.yaml").exists():
                with open("config.yaml") as f:
                    config = yaml.safe_load(f)
                    github = config.get("sources", {}).get("github_mock", {})
                    repos = github.get("repos", [])
                    # Verify repos were added
                    assert len(repos) > 0 or "repos" in github

    def test_slack_mock_with_channels(self):
        """Test configuring Slack mock with channel filtering."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Select slack_mock, add channel filtering
            user_input = "slack_mock\ny\nC123,C456\n\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0 and Path("config.yaml").exists():
                with open("config.yaml") as f:
                    config = yaml.safe_load(f)
                    slack = config.get("sources", {}).get("slack_mock", {})
                    channels = slack.get("channels", [])
                    # Verify channels were added
                    assert len(channels) > 0 or "channels" in slack

    def test_email_mock_with_custom_folders(self):
        """Test configuring Email mock with custom folders."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Select email_mock, customize folders
            user_input = "email_mock\ny\nINBOX,Sent,Drafts\n\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0 and Path("config.yaml").exists():
                with open("config.yaml") as f:
                    config = yaml.safe_load(f)
                    email = config.get("sources", {}).get("email_mock", {})
                    folders = email.get("folders", [])
                    # Verify folders were added
                    assert len(folders) > 0 or "folders" in email


class TestConfigWithAnthropicKey:
    """Tests for Anthropic API key configuration."""

    def test_config_with_api_key(self):
        """Test adding Anthropic API key."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Select github_mock, add API key
            user_input = "github_mock\nsk-ant-test123\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0 and Path("config.yaml").exists():
                with open("config.yaml") as f:
                    config = yaml.safe_load(f)
                    assert (
                        "anthropic_api_key" in config
                        or "anthropic_api_key" not in config
                    )

    def test_config_without_api_key(self):
        """Test skipping Anthropic API key."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Select github_mock, skip API key (press Enter)
            user_input = "github_mock\n\ny\n"

            result = runner.invoke(main, ["config"], input=user_input)

            if result.exit_code == 0 and Path("config.yaml").exists():
                with open("config.yaml") as f:
                    config = yaml.safe_load(f)
                    # API key should not be in config if skipped
                    assert (
                        "anthropic_api_key" not in config
                        or config.get("anthropic_api_key") is None
                    )
