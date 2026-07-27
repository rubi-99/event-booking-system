from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize slowapi limiter using remote client IP address as key
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])
