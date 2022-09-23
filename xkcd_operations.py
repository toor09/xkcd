import logging

from requests import Session

logger = logging.getLogger(__name__)


def get_image_info(session: Session, url: str) -> dict:
    """Get info for comic image."""
    comic_book = session.get(url=url)
    comic_book.raise_for_status()
    comic_book_info = comic_book.json()
    logger.debug(msg=f"{comic_book_info=}")
    return {
        "link": comic_book_info["img"],
        "comments": comic_book_info["alt"],
    }


def get_max_comic_id(session: Session, url: str) -> int:
    """Get comic max id for download of available comic."""
    current_comic = session.get(url=url)
    current_comic.raise_for_status()
    comic = current_comic.json()
    logger.debug(msg=f"{comic=}")
    return comic["num"]


def download_comic_image(
        session: Session,
        url: str,
        filename: str
) -> None:
    """ Download comic image from current page."""
    comic_book = session.get(url=url)
    comic_book.raise_for_status()

    with open(file=filename, mode="wb") as file:
        file.write(comic_book.content)
