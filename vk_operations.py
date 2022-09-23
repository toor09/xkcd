import logging

from requests import Session

logger = logging.getLogger(__name__)


def get_upload_url(
        session: Session,
        url: str,
        access_token: str,
        group_id: int
) -> str:
    """Get upload_url for uploading comic to VK storage."""
    payload = {
        "access_token": access_token,
        "group_id": group_id,
        "v": 5.131
    }
    server_info = session.post(url=url, data=payload)
    server_info.raise_for_status()
    uploaded_server_info = server_info.json()
    logger.debug(msg=f"{uploaded_server_info=}")
    return uploaded_server_info["response"]["upload_url"]


def upload_comic(
        session: Session,
        url: str,
        comic_path: str,
) -> dict:
    """Uploading comic to VK storage."""

    with open(file=comic_path, mode="rb") as comic:
        files = {"photo": comic}
        new_comic = session.post(url=url, files=files)
        new_comic.raise_for_status()
        uploaded_comic = new_comic.json()
    logger.debug(msg=f"{uploaded_comic=}")
    return {
        "photo": uploaded_comic["photo"],
        "server": uploaded_comic["server"],
        "hash": uploaded_comic["hash"]
    }


def save_comic(
        session: Session,
        url: str,
        access_token: str,
        group_id: int,
        comic: str,
        comic_hash: str,
        server: str
) -> dict:
    """Save comic to VK storage."""
    payload = {
        "server": server,
        "photo": comic,
        "hash": comic_hash,
        "access_token": access_token,
        "group_id": group_id,
        "v": 5.131
    }

    new_comic = session.post(url=url, data=payload)
    new_comic.raise_for_status()
    saved_comic = new_comic.json()
    logger.debug(msg=f"{saved_comic=}")
    return saved_comic


def publish_comic(
        session: Session,
        url: str,
        access_token: str,
        from_group: int,
        owner_id: int,
        attachments: str,
        message: str
) -> dict:
    """Publish comic to the wall of VK group."""
    payload = {
        "from_group": from_group,
        "owner_id": owner_id,
        "message": message,
        "attachments": attachments,
        "access_token": access_token,
        "v": 5.131
    }
    new_comic_post = session.post(url=url, data=payload)
    new_comic_post.raise_for_status()
    published_comic_post = new_comic_post.json()
    logger.debug(msg=f"{published_comic_post=}")
    return published_comic_post
