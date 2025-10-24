"""
Error handling and retry logic for the product export system.
"""

import time
import random
from typing import Callable, Any
from dataclasses import dataclass

class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

class TemporaryError(Exception):
    """Raised for temporary errors that can be retried"""
    pass

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0

class ErrorHandler:
    """Handles retries with exponential backoff and jitter"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.retry_config = RetryConfig(
            max_retries=config.processing.max_retries,
            base_delay=config.processing.retry_delay
        )
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic"""
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except RateLimitError as e:
                if attempt == self.retry_config.max_retries:
                    raise
                
                delay = self._calculate_delay(attempt, e.retry_after)
                self.logger.warning(f"Rate limited. Retrying in {delay}s (attempt {attempt + 1})")
                time.sleep(delay)
                
            except TemporaryError as e:
                if attempt == self.retry_config.max_retries:
                    raise
                
                delay = self._calculate_delay(attempt)
                self.logger.warning(f"Temporary error. Retrying in {delay}s (attempt {attempt + 1})")
                time.sleep(delay)
            
            except Exception as e:
                # For unexpected errors, don't retry
                self.logger.error(f"Unexpected error: {e}")
                raise
    
    def _calculate_delay(self, attempt: int, retry_after: int = None) -> float:
        """Calculate delay with exponential backoff and jitter"""
        if retry_after:
            return float(retry_after)
        
        delay = self.retry_config.base_delay * (2 ** attempt)
        jitter = random.uniform(0, 0.1) * delay
        return delay + jitter
