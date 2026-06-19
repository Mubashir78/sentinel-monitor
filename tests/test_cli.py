from pathlib import Path
from monitor.cli import init_config


def test_init_creates_file(tmp_path, monkeypatch):
    """sentinel init creates a targets.yaml with example content."""
    monkeypatch.chdir(tmp_path)

    init_config()

    config_file = tmp_path / "targets.yaml"
    assert config_file.exists()
    content = config_file.read_text()
    assert "sites:" in content
    assert "settings:" in content
