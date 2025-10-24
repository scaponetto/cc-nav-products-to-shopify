"""
Rate limiting compliance for Shopify API interactions.
"""

import time
import requests
from typing import Optional

class RateLimiter:
    """Handles Shopify API rate limiting"""
    
    def __init__(self, config):
        self.requests_per_second = config.processing.rate_limit_per_second
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < (1.0 / self.requests_per_second):
            sleep_time = (1.0 / self.requests_per_second) - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def handle_rate_limit_response(self, response: requests.Response) -> bool:
        """Handle 429 responses with Retry-After header"""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 2))
            print(f"Rate limited. Waiting {retry_after} seconds")
            time.sleep(retry_after)
            return True
        return False
