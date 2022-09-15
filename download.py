from typing import Optional

from requests import Session


def get_image_info(session: Session, url: str) -> dict:
    """Get info for comic image."""
    comic_book = session.get(url=url)
    comic_book.raise_for_status()
    comic_book_info = comic_book.json()

    return {
        "link": comic_book_info.get("img"),
        "comments": comic_book_info.get("alt"),
    }


def download_comic_image(
        session: Session,
        url: Optional[str],
        filename: str
) -> None:
    """ Download comic image from current page."""
    if url:
        comic_book = session.get(url=url)
        comic_book.raise_for_status()

        with open(file=filename, mode="wb") as file:
            file.write(comic_book.content)
    return None
