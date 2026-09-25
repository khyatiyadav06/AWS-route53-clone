from datetime import datetime, timezone, timedelta
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Session as UserSession
from app.schemas.auth import LoginRequest, LoginResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
DEMO_PASSWORD = "Route53Demo123"
SESSION_HOURS = 24

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not secrets.compare_digest(payload.password, DEMO_PASSWORD):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Keep one active demo session per token; old sessions naturally expire.
    token = secrets.token_urlsafe(48)
    db.add(UserSession(token=token, user_id=user.id, expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=SESSION_HOURS)))
    db.commit()
    return {"token": token, "user": user}

@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            db.delete(session)
            db.commit()
    return {"message": "Logged out"}

@router.get("/session", response_model=UserOut)
def session(user: User = Depends(get_current_user)):
    return user
