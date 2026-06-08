import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

def get_user_id_or_ip(request: Request) -> str:
    """
    Extracts the Supabase user ID from the JWT token in the Authorization header.
    Falls back to the IP address if no valid token is found.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # We decode the payload without verifying the signature
            # because your actual Auth dependency rejects invalid tokens anyway.
            # We just need the ID for rate limiting.
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            # If the token is malformed, we fall through to IP limiting
            pass
            
    # Fallback for unauthenticated users
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_id_or_ip)