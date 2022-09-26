import os
from pathlib import Path
from typing import Union

import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings, XKCDSettings


def get_session(
        settings: Settings
) -> requests.Session:
    """Returned new request session with retry strategy."""
    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def sanitize_file_path(file_path: Union[Path, str], file_name: str) -> str:
    """Sanitize file path."""
    sanitized_file_path = os.path.join(
        sanitize_filepath(file_path=file_path, platform="auto"),
        sanitize_filename(filename=file_name, platform="auto")
    )
    return sanitized_file_path


def create_dirs(settings: XKCDSettings) -> None:
    """Creates dirs for downloaded files."""
    images_path = sanitize_filepath(
        file_path=settings.COMICS_PATH,
        platform="auto"
    )
    os.makedirs(name=images_path, exist_ok=True)


def remove_comic(comic_path: Union[Path, str], comic_filename: str) -> None:
    """Remove comic file."""
    sanitized_file_path = sanitize_file_path(
        file_path=comic_path,
        file_name=comic_filename
    )
    if os.path.isfile(sanitized_file_path):
        os.remove(sanitized_file_path)
