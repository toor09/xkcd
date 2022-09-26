import logging
import logging.config
import os
import time
from pathlib import Path
from random import randint

from pathvalidate import sanitize_filename, sanitize_filepath
from requests import ConnectionError, HTTPError

from settings import LOGGING_CONFIG, Settings, VKSettings, XKCDSettings
from utils import get_session
from vk_operations import (
    get_upload_url,
    publish_comic,
    save_comic,
    upload_comic
)
from xkcd_operations import (
    download_comic_image,
    get_image_comic,
    get_max_comic_id
)

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG)


def main() -> None:
    """Main entry for publishing comics in group VK."""
    settings = Settings()
    xkcd_settings = XKCDSettings()
    vk_settings = VKSettings()
    session = get_session(settings=settings)
    try:
        max_comic_id = get_max_comic_id(
            session=session,
            url=f"{xkcd_settings.XKCD_BASE_URL}{xkcd_settings.XKCD_BASE_URI}"
        )

        random_comic_id = randint(1, max_comic_id)
        comic_url = f"{xkcd_settings.XKCD_BASE_URL}/{random_comic_id}" \
                    f"{xkcd_settings.XKCD_BASE_URI}"

        image_comic = get_image_comic(session=session, url=comic_url)

        comic_file_name = sanitize_filename(
            filename=Path(image_comic["link"]).name,
            platform="auto"
        )
        comic_filepath = sanitize_filepath(
            file_path=comic_file_name,
            platform="auto"
        )
        download_comic_image(
            session=session,
            url=image_comic["link"],
            filename=comic_filepath  # type: ignore
        )
        message = f"Был скачан комикс `{comic_file_name}`. " \
                  f"Комментарии: {image_comic['comments']}"
        logger.debug(msg=message)

        upload_comic_url = get_upload_url(
            session=session,
            access_token=vk_settings.VK_ACCESS_TOKEN,
            group_id=vk_settings.VK_GROUP_ID,
            version=vk_settings.VK_VERSION
        )
        uploaded_comic = upload_comic(
            session=session,
            url=upload_comic_url,
            comic_path=comic_filepath  # type: ignore
        )
        saved_comic = save_comic(
            session=session,
            access_token=vk_settings.VK_ACCESS_TOKEN,
            group_id=vk_settings.VK_GROUP_ID,
            comic=uploaded_comic["photo"],
            comic_hash=uploaded_comic["hash"],
            server=uploaded_comic["server"],
            version=vk_settings.VK_VERSION
        )
        owner_id = saved_comic["response"][0]["owner_id"]
        media_id = saved_comic["response"][0]["id"]
        publish_comic(
            session=session,
            access_token=vk_settings.VK_ACCESS_TOKEN,
            owner_id=vk_settings.VK_GROUP_ID,
            attachments=f"photo{owner_id}_{media_id}",
            message=image_comic['comments'],
            version=vk_settings.VK_VERSION
        )

    except HTTPError as err:
        logger.exception(msg=err)

    except ConnectionError as err:
        message = f"Ошибка подключения :( {err}"
        logger.exception(msg=message)
        time.sleep(settings.TIMEOUT)

    finally:
        os.remove(path=comic_filepath)


if __name__ == "__main__":
    main()
