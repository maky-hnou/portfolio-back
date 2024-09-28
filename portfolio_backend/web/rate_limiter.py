"""Module for configuring the SlowAPI rate limiter.

This module sets up a global rate limiter using SlowAPI with Redis
as the storage backend. It defines the function to get the remote
address of clients and enables header responses for rate limiting.

Dependencies:
    - Limiter: Class for creating a rate limiter.
    - get_remote_address: Function for retrieving the client's IP address.

Attributes:
    limiter (Limiter): A global rate limiter instance configured
    to use Redis for storage and to retrieve the remote address.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure the SlowAPI Limiter globally
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/0", headers_enabled=True)
