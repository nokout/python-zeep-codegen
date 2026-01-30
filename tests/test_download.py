"""
Unit tests for the download module.

Tests the download_from_url function with mocked HTTP requests.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import requests

from pipeline.download import download_from_url
from exceptions import DownloadError


@pytest.mark.unit
def test_download_from_url_success(temp_test_dir: Path) -> None:
    """Test successful download from URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<xml>test</xml>'
    mock_response.headers = {'content-type': 'application/xml'}
    
    with patch('requests.get', return_value=mock_response):
        with patch('pipeline.download.Path', return_value=temp_test_dir):
            result = download_from_url('https://example.com/test.wsdl')
            
            assert result is not None
            assert isinstance(result, Path)


@pytest.mark.unit
def test_download_from_url_timeout() -> None:
    """Test download timeout handling."""
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(DownloadError, match="timed out"):
            download_from_url('https://example.com/test.wsdl', timeout=5)


@pytest.mark.unit
def test_download_from_url_connection_error() -> None:
    """Test connection error handling."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(DownloadError, match="Could not connect"):
            download_from_url('https://example.com/test.wsdl')


@pytest.mark.unit
def test_download_from_url_http_error() -> None:
    """Test HTTP error handling."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.reason = 'Not Found'
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(DownloadError, match="HTTP 404"):
            download_from_url('https://example.com/test.wsdl')


@pytest.mark.unit
def test_download_from_url_filename_detection() -> None:
    """Test filename detection from URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<xml>test</xml>'
    mock_response.headers = {'content-type': 'application/xml'}
    
    with patch('requests.get', return_value=mock_response):
        result = download_from_url('https://example.com/myservice.wsdl')
        
        assert result.name == 'myservice.wsdl'


@pytest.mark.unit
def test_download_from_url_generic_filename() -> None:
    """Test generic filename when no extension in URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<xml>test</xml>'
    mock_response.headers = {'content-type': 'application/xml'}
    
    with patch('requests.get', return_value=mock_response):
        result = download_from_url('https://example.com/service?wsdl')
        
        # Should use generic name for WSDL
        assert 'downloaded' in result.name
