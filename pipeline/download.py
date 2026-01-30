"""
Pipeline module for downloading WSDL/XSD files from URLs.

This module provides functionality to download XSD/WSDL files from HTTP/HTTPS URLs,
with proper timeout handling and error reporting.
"""
import logging
import requests
from pathlib import Path
from urllib.parse import urlparse, ParseResult
from typing import Final

from exceptions import DownloadError

logger: logging.Logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT: Final[int] = 30
TEMP_DIR: Final[str] = ".temp"
DOWNLOADS_SUBDIR: Final[str] = "downloads"


def download_from_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> Path:
    """
    Download XSD/WSDL file from HTTP/HTTPS URL to temporary location.
    
    Downloads a file from the specified URL and saves it to a temporary directory
    with proper filename detection from the URL or Content-Disposition header.
    
    Args:
        url: HTTP/HTTPS URL to download from
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Path to downloaded file in temp directory
    
    Raises:
        DownloadError: If download fails due to timeout, connection error,
                      HTTP error, or other issues
    
    Example:
        >>> path = download_from_url('https://example.com/service.wsdl')
        >>> print(path)
        .temp/downloads/service.wsdl
    """
    logger.info(f"Downloading from URL: {url}")
    
    try:
        response: requests.Response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Determine filename from URL or Content-Disposition header
        parsed_url: ParseResult = urlparse(url)
        filename: str = Path(parsed_url.path).name
        
        # If no filename in URL, use generic name based on content type
        if not filename or '.' not in filename:
            content_type: str = response.headers.get('content-type', '')
            if 'xml' in content_type.lower() or 'wsdl' in url.lower():
                filename = 'downloaded.wsdl' if 'wsdl' in url.lower() else 'downloaded.xsd'
            else:
                filename = 'downloaded.xml'
        
        # Save to temp directory (use downloads subdirectory to avoid conflicts)
        temp_dir: Path = Path(TEMP_DIR)
        downloads_dir: Path = temp_dir / DOWNLOADS_SUBDIR
        downloads_dir.mkdir(parents=True, exist_ok=True)
        file_path: Path = downloads_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
        logger.info(f"Saved to: {file_path}")
        
        return file_path
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out after {timeout} seconds"
        logger.error(error_msg)
        raise DownloadError(error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = f"Could not connect to {url}"
        logger.error(error_msg)
        raise DownloadError(error_msg)
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code} - {e.response.reason}"
        logger.error(error_msg)
        raise DownloadError(error_msg)
    except Exception as e:
        error_msg = f"Error downloading file: {e}"
        logger.error(error_msg)
        raise DownloadError(error_msg)
