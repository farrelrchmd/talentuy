"""Dependency autentikasi dan otorisasi berbasis role."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

ROLE_RANK = {"viewer": 1, "analyst": 2, "admin": 3}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi tidak ditemukan. Silakan masuk kembali.",
        )
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi tidak valid atau telah berakhir.",
        )
    user = db.get(User, payload.get("sub", ""))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun tidak aktif atau tidak ditemukan.",
        )
    return user


def require_role(minimum: str) -> Callable[[User], User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if ROLE_RANK.get(user.role, 0) < ROLE_RANK[minimum]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki izin untuk tindakan ini.",
            )
        return user

    return dependency


require_analyst = require_role("analyst")
require_admin = require_role("admin")


def write_audit(
    db: Session,
    user: User | None,
    action: str,
    entity: str = "",
    entity_id: str = "",
    detail: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=user.id if user else None,
            actor_email=user.email if user else "",
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail or {},
        )
    )
