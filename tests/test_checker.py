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


@pytest.mark.asyncio
async def test_request_error(site):
    """A network error marks the site as down with an error message."""
    import httpx

    mock_client = AsyncMock()
    mock_client.head.side_effect = httpx.RequestError("DNS resolution failed")

    with patch("monitor.checker.get_ssl_expiry_days", return_value="DNS Lookup Failed"):
        result = await check_uptime(mock_client, site)

    assert result.is_up is False
    assert result.status_code == 0
    assert "DNS resolution failed" in result.error_msg


@pytest.mark.asyncio
async def test_run_all_checks_returns_all_results():
    """All sites are checked and results returned for each."""
    sites = [
        SiteConfig(name="Site One", url="https://one.example.com"),
        SiteConfig(name="Site Two", url="https://two.example.com"),
    ]

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("monitor.checker.get_ssl_expiry_days", return_value=90), \
         patch("httpx.AsyncClient.head", new_callable=AsyncMock, return_value=mock_response):
        results = await run_all_checks(sites, timeout=5)

    assert len(results) == 2
    assert all(isinstance(r, SiteResult) for r in results)
    assert all(r.is_up for r in results)
