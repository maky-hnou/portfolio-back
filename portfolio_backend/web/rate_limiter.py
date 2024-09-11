from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure the SlowAPI Limiter globally
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/0", headers_enabled=True)
