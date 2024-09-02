from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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

LOGIN_BONUS = 100
