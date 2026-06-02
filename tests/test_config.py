from monitor.config import load_config


def test_config():
    config = load_config()

    assert config is not None
    assert config.timeout == 5
