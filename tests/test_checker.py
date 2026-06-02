import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from monitor.checker import check_uptime, run_all_checks, SiteResult
from monitor.config import SiteConfig

@pytest.fixture
def site():
    return SiteConfig(name="Test Site", url="https://example.com")


@pytest.mark.asyncio
async def test_site_is_up(site):
    """A 200 response marks the site is up."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.head.return_value = mock_response

    with patch("monitor.checker.get_ssl_expiry_days", return_value=60):
        result = await check_uptime(mock_client, site)


    assert result.is_up is True
    assert result.status_code == 200
    assert result.name == "Test Site"
    assert result.url == "https://example.com"
    assert result.ssl_days_left == 60
    assert result.error_msg == ""


@pytest.mark.asyncio
async def test_site_is_down(site):
    """A 4xx response marks the site as down."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client = AsyncMock()
    mock_client.head.return_value = mock_response

    with patch("monitor.checker.get_ssl_expiry_days", return_value=60):
        result = await check_uptime(mock_client, site)

    assert result.is_up is False
    assert result.status_code == 404
    assert result.error_msg == ""
