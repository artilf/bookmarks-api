from typing import List, Optional

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
    return {"status_code": 200, "headers": {"Content-Type": "plain/html"}, "body": page}


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


def create_html_until_head(title: str, redirect_url: Optional[str] = None) -> List[str]:
    fist_half = [
        "<!DOCTYPE html>",
        '<html lang="ja-jp">',
        "<head>",
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width" />',
        f"  <title>{title}</title>",
    ]
    second_half = [
        "</head>",
    ]
    if redirect_url is None:
        return fist_half + second_half
    else:
        return (
            fist_half
            + [f'<meta http-equiv="refresh" content="{SECOND};URL={redirect_url}">']
            + second_half
        )


def create_article_block(article: Article) -> List[str]:
    return [
        f"  <hr />",
        f"  <div>",
        f'    <p>URL: <a href="{article.url}" target="_blank">{article.url}</a><p>',
        f'    <p>Title: <a href="{article.url}" target="_blank">{article.title}</a><p>',
        f"  </div>",
    ]


def create_error_page(message: str, article: Optional[Article]) -> str:
    until_head = create_html_until_head("Failed Regist Article")
    first_half_body = [
        "<body>",
        "  <h2>Failed Regist Article</h2>",
    ]
    article_block = create_article_block(article) if article is not None else []
    second_half_body = [
        "  <hr />",
        "  <div>",
        "    <h3>Error Message</h3>",
        f"    <pre>{message}</pre>",
        "  </div>",
        "</body>",
    ]
    return "\n".join(
        until_head + first_half_body + article_block + second_half_body + ["</html>"]
    )


def create_success_page(article: Optional[Article]) -> str:
    url = article.url if article is not None else None
    article_block = create_article_block(article) if article is not None else []
    until_head = create_html_until_head("Success Regist Article", url)
    first_half_body = [
        "<body>",
        "  <h2>Success Regist Article</h2>",
    ]
    seonc_half_body = ["</body>", "</html>"]
    return "\n".join(until_head + first_half_body + article_block + seonc_half_body)
