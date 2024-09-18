from pathlib import Path

import redis.asyncio as redis
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


auth_jwt = AuthJWT()

PRIVATE_KEY = auth_jwt.private_key_path.read_text()
PUBLIC_KEY = auth_jwt.public_key_path.read_text()

MAX_ATTEMPTS = 3
BLOCK_TIME_SECONDS = 300

REDIS_URL = "redis://redis:6379/0"

redis_client = redis.from_url(
    REDIS_URL, encoding="utf-8", decode_responses=True
)

LOGIN_BONUS = 100
