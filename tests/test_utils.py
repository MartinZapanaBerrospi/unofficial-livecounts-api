import pytest
import httpx
from unofficial_livecounts_api.error import RequestApiError
from unofficial_livecounts_api.utils import send_request, async_send_request


def test_send_request_when_server_response_true(mocker):
    # Mock synchronous httpx client
    mock_get = mocker.patch("unofficial_livecounts_api.utils.http_client.get")
    mock_get.return_value = httpx.Response(200, content=b'{"success": true}')
    
    data = send_request(url="http://test.test")
    mock_get.assert_called_once_with(url="http://test.test", headers=mocker.ANY)
    assert data == {"success": True}


def test_send_request_when_server_response_false(mocker):
    mock_get = mocker.patch("unofficial_livecounts_api.utils.http_client.get")
    mock_get.return_value = httpx.Response(403, content=b'{"success": false}')
    
    with pytest.raises(RequestApiError) as exec_info:
        send_request(url="http://test.test")
    
    assert "Server rejected request with status: 403" in str(exec_info.value)


def test_send_request_when_server_response_error(mocker):
    mock_get = mocker.patch("unofficial_livecounts_api.utils.http_client.get")
    mock_get.return_value = httpx.Response(500, content=b'{"error": "internal"}')
    
    with pytest.raises(RequestApiError) as exec_info:
        send_request(url="http://test.test")
        
    assert "Server rejected request with status: 500" in str(exec_info.value)


@pytest.mark.asyncio
async def test_async_send_request_true(mocker):
    # Mock asynchronous httpx client
    mock_get = mocker.patch("unofficial_livecounts_api.utils.async_http_client.get", new_callable=mocker.AsyncMock)
    mock_get.return_value = httpx.Response(200, content=b'{"success": true}')
    
    data = await async_send_request(url="http://test.test")
    mock_get.assert_called_once_with(url="http://test.test", headers=mocker.ANY)
    assert data == {"success": True}
