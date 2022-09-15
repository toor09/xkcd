import logging
import logging.config

from download import download_comic_image, get_image_info
from settings import LOGGING_CONFIG, Settings
from utils import create_dirs, get_file_name, get_session, sanitize_file_path

logger = logging.getLogger(__file__)
logging.config.dictConfig(LOGGING_CONFIG)


def main() -> None:
    """Main entry for publishing comic books in group VK."""
    settings = Settings()
    create_dirs(settings=settings)
    session = get_session(settings=settings)
    image_info = get_image_info(session=session, url=settings.XKCD_URL)
    if image_info["link"]:
        comic_file_name = get_file_name(url=image_info["link"])
        comic_file_path = sanitize_file_path(
            file_path=settings.COMICS_PATH,
            file_name=comic_file_name
        )
        download_comic_image(
            session=session,
            url=image_info["link"],
            filename=comic_file_path
        )
        message = f"Был скачан комикс `{comic_file_name}`. " \
                  f"Комментарии: {image_info['comments']}"
        logger.debug(msg=message)


if __name__ == "__main__":
    main()
