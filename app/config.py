import os
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv()


class Config(BaseModel):
    DB_CONFIG: str = os.getenv(
        "DB_CONFIG",
        "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.getenv("DB_USER"),
            DB_PASSWORD=os.getenv("DB_PASSWORD"),
            DB_HOST=os.getenv("DB_HOST"),
            DB_NAME=os.getenv("DB_NAME"),
        ),
    ),
    TEST_DB_CONFIG: str = os.getenv(
        "TEST_DB_CONFIG",
        "postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}/{TEST_DB_NAME}".format(
            TEST_DB_USER=os.getenv("TEST_DB_USER"),
            TEST_DB_PASSWORD=os.getenv("TEST_DB_PASSWORD"),
            TEST_DB_HOST=os.getenv("TEST_DB_HOST"),
            TEST_DB_NAME=os.getenv("TEST_DB_NAME"),
        ),
    )


config = Config()


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"

    access_token_algorithm: str = os.getenv("ACCESS_TOKEN_ALGORITHM", "RS256")
    access_token_secret_key: str = os.getenv("ACCESS_TOKEN_SECRET_KEY")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 15))


auth_jwt_config = AuthJWT()


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:252525@localhost:5432/fast_poetry"
    database_config: Config = config
    echo_sql: bool = True
    test: bool = False
    project_name: str = "full_fast_api"

    oath_token_secret: Optional[str] = os.getenv("OATH_TOKEN_SECRET_KEY")
    auth_jwt: AuthJWT = auth_jwt_config

    log_level: str = "DEBUG"


settings = Settings()
