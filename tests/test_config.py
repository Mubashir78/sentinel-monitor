import pytest
from monitor.config import load_config, AppConfig, SiteConfig


def test_config():
    config = load_config()

    assert config is not None
    assert config.timeout == 5


def test_load_valid_config(tmp_path):
    """Valid config loads correctly into typed dataclasses."""
    config_file = tmp_path / "targets.yaml"
    config_file.write_text("""
settings:
  timeout: 10
  alert_webhook: ""

sites:
  - name: "Google"
    url: "https://google.com"
  - name: "My API"
    url: "https://api.example.com"
""")

    config = load_config(str(config_file))

    assert isinstance(config, AppConfig)
    assert config.timeout == 10
    assert config.webhook_url == ""
    assert len(config.sites) == 2
    assert isinstance(config.sites[0], SiteConfig)
    assert config.sites[0].name == "Google"
    assert config.sites[0].url == "https://google.com"


def test_load_config_defaults(tmp_path):
    """Config uses default timeout when settings block is missing."""
    config_file = tmp_path / "targets.yaml"
    config_file.write_text("""
sites:
  - name: "Google"
    url: "https://google.com"
""")
    config = load_config(str(config_file))

    assert config.timeout == 5
    assert config.webhook_url is None


def test_missing_file():
    """Missing config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")
