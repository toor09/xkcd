import logging
from pathlib import Path
from typing import Tuple, Union

from pathvalidate import sanitize_filename, sanitize_filepath
from requests import Session

logger = logging.getLogger(__name__)


def get_max_comic_id(session: Session, url: str) -> int:
    """Get comic max id for download of available comic."""
    current_comic = session.get(url=url)
    current_comic.raise_for_status()
    comic = current_comic.json()
    logger.debug(msg=f"{comic=}")
    return comic["num"]


def download_comic_image(
        session: Session,
        comic_id: int
) -> Tuple[str, Union[str, Path]]:
    """Download comic image from current page."""
    comic_book = session.get(url=f"https://xkcd.com/{comic_id}/info.0.json")
    comic_book.raise_for_status()
    image_comic = comic_book.json()
    logger.debug(msg=f"{image_comic=}")

    comic_file_name = sanitize_filename(
        filename=Path(image_comic["img"]).name,
        platform="auto"
    )
    comic_filepath = sanitize_filepath(
        file_path=comic_file_name,
        platform="auto"
    )
    comic_book = session.get(url=image_comic["img"])
    comic_book.raise_for_status()

    with open(file=comic_file_name, mode="wb") as file:
        file.write(comic_book.content)
    return image_comic["alt"], comic_filepath
