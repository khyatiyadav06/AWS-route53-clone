from datetime import datetime, timezone
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models import Session as UserSession, User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: DBSession = Depends(get_db),
) -> User:
    """Resolve and validate the authenticated user from a Bearer session token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    session = db.query(UserSession).filter(UserSession.token == token).first()
    if not session or session.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None):
        if session:
            db.delete(session)
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")

    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
