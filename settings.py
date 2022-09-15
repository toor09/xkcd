import sys
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    COMICS_PATH: Path = Path("comics")
    XKCD_URL: AnyHttpUrl
    RETRY_COUNT: int = 5
    STATUS_FORCE_LIST: str = "429,500,502,503,504"
    ALLOWED_METHODS: str = "HEAD,GET,OPTIONS"
    LOGGING_LEVEL: str = "ERROR"

    @validator("STATUS_FORCE_LIST")
    def status_force_list(cls, v: str) -> List[int]:
        if isinstance(v, str):
            return [int(_v.strip()) for _v in v.split(",")]

    @validator("ALLOWED_METHODS")
    def allowed_methods(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [_v.strip() for _v in v.split(",")]

    @validator("LOGGING_LEVEL")
    def logging_levels(cls, v: str) -> str:
        if v.upper() not in LEVELS:
            raise ValueError(
                f"The value is not in the list of required: {LEVELS}"
            )
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": Settings().LOGGING_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
        },
        "rotating_to_file": {
            "level": Settings().LOGGING_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "xkcd.log",
            "maxBytes": 10000,
            "backupCount": 10,
        },
    },
    "loggers": {
        "main": {
            "handlers": ["default", "rotating_to_file"],
            "level": Settings().LOGGING_LEVEL,
            "propagate": True
        }
    }
}
