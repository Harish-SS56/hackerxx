from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify the Bearer token from the Authorization header
    """
    try:
        token = credentials.credentials
        
        if not token:
            logger.warning("No token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token != settings.SECRET_API_KEY:
            logger.warning(f"Invalid token provided: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Token verified successfully")
        return token
        
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
