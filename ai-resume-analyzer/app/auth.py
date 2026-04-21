import hashlib
import hmac
import bcrypt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import jwt

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SECRET_KEY = "resume-intelligence-super-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


# ─────────────────────────────────────────
# HELPER — sha256 pre-hash so bcrypt never
# sees more than 64 bytes (hex digest = 64 chars)
# ─────────────────────────────────────────
def _prehash(plain_password: str) -> bytes:
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest().encode("utf-8")


# ─────────────────────────────────────────
# PASSWORD UTILITIES
# ─────────────────────────────────────────
def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(_prehash(plain_password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_prehash(plain_password), hashed_password.encode("utf-8"))


# ─────────────────────────────────────────
# JWT TOKEN UTILITIES
# ─────────────────────────────────────────
def create_access_token(user_id: int, email: str, username: str) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Please log in again.",
        )