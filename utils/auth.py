from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import get_settings

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    This function verifies the JWT token sent by the client.
    It checks if the token is expired, invalid, or tampered with.
    If the token is valid, it returns the payload.
    If the token is invalid, it raises an HTTPException.
    
    Args:
        credentials: The JWT token sent by the client.
    
    Returns:
        The payload of the JWT token if valid.
    
    Raises:
        HTTPException: If the token is expired, invalid, or tampered with.
    """
    settings = get_settings()
    
    try:
        token = credentials.credentials
        
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")
        
        if alg == "HS256":
            if not settings.supabase_jwt_secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWT secret not configured for HS256 verification."
                )
            key = settings.supabase_jwt_secret
        elif alg in ["ES256", "RS256"]:
            # Supabase uses asymmetric keys, so we fetch the public key via JWKS
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            issuer = unverified_payload.get("iss")
            
            if not issuer or ".supabase.co" not in issuer:
                raise jwt.InvalidTokenError("Invalid issuer for asymmetric token")
                
            jwks_url = f"{issuer}/.well-known/jwks.json"
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            key = signing_key.key
        else:
            raise jwt.InvalidTokenError(f"Unsupported algorithm: {alg}")

        payload = jwt.decode(
            token, 
            key, 
            algorithms=["HS256", "ES256", "RS256"],
            audience="authenticated" 
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
