from pathlib import Path
from typing import Optional

from jinja2 import Template

from logger.my_logger import MyLogger
from models.article import Article
from tools.base64 import urlsafe_decode
from tools.bookmarklet_tools import (
    get_raw_encoded_article,
    get_raw_encoded_message,
    is_success,
)

logger = MyLogger(__name__)
SECOND = 5


def main(event):
    article = get_article(event)
    if is_success(event):
        page = create_success_page(article)
        return create_response(page)
    else:
        message = get_message(event)
        page = create_error_page(message, article)
        return create_response(page)


def create_response(page: str):
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": page}


def get_article(event) -> Optional[Article]:
    raw_encoded_article = get_raw_encoded_article(event)
    if raw_encoded_article is None:
        return None
    try:
        text = urlsafe_decode(raw_encoded_article).decode()
        return Article.loads(text)
    except Exception as e:
        logger.warning(f"Exception occurred: {e}")
        return None


def get_message(event) -> str:
    raw_encoded_message = get_raw_encoded_message(event)
    if raw_encoded_message is None:
        return str(None)
    return urlsafe_decode(raw_encoded_message).decode()


def get_failed_template():
    rel_path = "templates/failed.html.j2"
    path = Path(__file__).parent.joinpath(rel_path).resolve()
    return open(str(path)).read()


def get_success_template():
    rel_path = "templates/success.html.j2"
    path = Path(__file__).parent.joinpath(rel_path).resolve()
    return open(str(path)).read()


def create_error_page(message: str, article: Optional[Article]) -> str:
    template = Template(get_failed_template())
    return template.render(message=message, article=article)


def create_success_page(article: Optional[Article]) -> str:
    template = Template(get_success_template())
    return template.render(article=article)
