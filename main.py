import logging
import logging.config
import time
from random import randint

from requests import ConnectionError, HTTPError

from settings import LOGGING_CONFIG, Settings, VKSettings, XKCDSettings
from utils import (
    create_dirs,
    get_file_name,
    get_session,
    remove_comic,
    sanitize_file_path
)
from vk_operations import (
    get_upload_url,
    publish_comic,
    save_comic,
    upload_comic
)
from xkcd_operations import (
    download_comic_image,
    get_image_info,
    get_max_comic_id
)

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG)


def main() -> None:
    """Main entry for publishing comics in group VK."""
    settings = Settings()
    xkcd_settings = XKCDSettings()
    vk_settings = VKSettings()
    create_dirs(settings=xkcd_settings)
    session = get_session(settings=settings)
    try:
        max_comic_id = get_max_comic_id(
            session=session,
            url=f"{xkcd_settings.XKCD_BASE_URL}{xkcd_settings.XKCD_BASE_URI}"
        )

        random_comic_id = randint(1, max_comic_id)
        comic_url = f"{xkcd_settings.XKCD_BASE_URL}/{random_comic_id}" \
                    f"{xkcd_settings.XKCD_BASE_URI}"

        image_info = get_image_info(session=session, url=comic_url)

        comic_file_name = get_file_name(url=image_info["link"])
        comic_file_path = sanitize_file_path(
            file_path=xkcd_settings.COMICS_PATH,
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

        upload_comic_url = get_upload_url(
            session=session,
            url=f"{vk_settings.VK_API_URL}photos.getWallUploadServer",
        )
        uploaded_comic = upload_comic(
            session=session,
            url=upload_comic_url,
            comic_path=sanitize_file_path(
                file_path=xkcd_settings.COMICS_PATH,
                file_name=comic_file_name
            )
        )
        saved_comic = save_comic(
            session=session,
            url=f"{vk_settings.VK_API_URL}photos.saveWallPhoto",
            comic=uploaded_comic["photo"],
            comic_hash=uploaded_comic["hash"],
            server=uploaded_comic["server"],
        )
        owner_id = saved_comic["response"][0]["owner_id"]
        media_id = saved_comic["response"][0]["id"]
        published_comic = publish_comic(
            session=session,
            url=f"{vk_settings.VK_API_URL}wall.post",
            from_group=1,
            owner_id=-vk_settings.VK_GROUP_ID,
            attachments=f"photo{owner_id}_{media_id}",
            message=image_info['comments']
        )
        if published_comic["response"]['post_id']:
            remove_comic(
                comic_path=xkcd_settings.COMICS_PATH,
                comic_filename=comic_file_name
            )

    except HTTPError as err:
        logger.exception(msg=err)

    except ConnectionError as err:
        message = f"Ошибка подключения :( {err}"
        logger.exception(msg=message)
        time.sleep(settings.TIMEOUT)


if __name__ == "__main__":
    main()
