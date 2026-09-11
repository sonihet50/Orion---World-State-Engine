from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_db() -> Generator[Session, None, None]:
    """Provides request-scoped database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extracts authenticated user if JWT token is provided, otherwise None."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user_repo = UserRepository(db)
    return user_repo.get(user_id)

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Enforces authentication; raises 401 if missing or invalid."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise credentials_exception
    return user
