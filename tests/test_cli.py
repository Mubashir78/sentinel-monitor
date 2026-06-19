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


def test_init_warns_if_exists(tmp_path, monkeypatch, capsys):
    """Sentinel init does not overwrite an existing targets.yaml."""
    monkeypatch.chdir(tmp_path)

    config_file = tmp_path / "targets.yaml"
    config_file.write_text("original content")

    init_config()

    captured = capsys.readouterr()
    assert "already exists" in captured.out
    assert config_file.read_text() == "original content"
