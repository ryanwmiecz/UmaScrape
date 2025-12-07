"""
HTTP client abstraction with retry logic and proper error handling.
Eliminates duplicate request code throughout the application.
"""
import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from utils import get_logger


logger = get_logger(__name__)


class HTTPClient:
    """
    HTTP client with built-in retry logic, timeout, and error handling.
    Centralizes all HTTP communication in the application.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None
    ):
        """
        Initialize HTTP client with configuration.
        
        Args:
            timeout: Request timeout in seconds (uses settings default if None)
            max_retries: Maximum retry attempts (uses settings default if None)
            user_agent: User agent string (uses settings default if None)
        """
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.user_agent = user_agent or settings.USER_AGENT
        
        # Create session with retry strategy
        self.session = self._create_session()
        
        logger.debug(f"HTTPClient initialized (timeout={self.timeout}s, retries={self.max_retries})")
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry configuration.
        
        Returns:
            Configured session object
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': self.user_agent
        })
        
        return session
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Perform GET request with error handling and logging.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Additional headers (merged with defaults)
            timeout: Override default timeout
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: On request failure after retries
        """
        request_timeout = timeout or self.timeout
        
        try:
            logger.debug(f"GET {url} (timeout={request_timeout}s)")
            start_time = time.time()
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=request_timeout
            )
            
            elapsed = time.time() - start_time
            logger.info(f"GET {url} -> {response.status_code} ({elapsed:.2f}s)")
            
            response.raise_for_status()
            return response
        
        except requests.Timeout as e:
            logger.error(f"Request timeout after {request_timeout}s: {url}")
            raise requests.RequestException(f"Request timed out after {request_timeout} seconds") from e
        
        except requests.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {url}")
            raise
        
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {str(e)}")
            raise
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Perform POST request with error handling and logging.
        
        Args:
            url: Target URL
            data: Form data
            json: JSON data
            headers: Additional headers
            timeout: Override default timeout
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: On request failure
        """
        request_timeout = timeout or self.timeout
        
        try:
            logger.debug(f"POST {url}")
            start_time = time.time()
            
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=request_timeout
            )
            
            elapsed = time.time() - start_time
            logger.info(f"POST {url} -> {response.status_code} ({elapsed:.2f}s)")
            
            response.raise_for_status()
            return response
        
        except requests.RequestException as e:
            logger.error(f"POST request failed: {url} - {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
            logger.debug("HTTPClient session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
