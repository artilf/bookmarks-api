from base64 import urlsafe_b64decode
from datetime import datetime, timezone
from typing import Optional

from boto3.resources.base import ServiceResource
from botocore.client import BaseClient

from logger.my_logger import MyLogger
from models.article import Article
from models.posted_config import PostedConfig
from tools.auth import can_access
from tools.aws_tools import get_dynamodb_resource, get_kms_client, get_ssm_client
from tools.bookmarklet_tools import (
    create_failed_response,
    create_success_response,
    get_raw_encoded_article,
    get_raw_encoded_config,
)
from tools.environment_values import get_articles_table_name, get_user_id

logger = MyLogger(__name__)


class BadRequestError(Exception):
    pass


def main(
    event,
    arg_ssm_client: Optional[BaseClient] = None,
    arg_kms_client: Optional[BaseClient] = None,
    arg_dynamodb_resource: Optional[ServiceResource] = None,
):
    ssm_client: BaseClient = get_ssm_client() if arg_ssm_client is None else arg_ssm_client
    kms_client: BaseClient = get_kms_client() if arg_kms_client is None else arg_kms_client
    dynamodb_resource: ServiceResource = get_dynamodb_resource() if arg_dynamodb_resource is None else arg_dynamodb_resource

    if not can_access(event, ssm_client):
        return create_failed_response("Forbidden")

    raw_encoded_article = get_raw_encoded_article(event)
    raw_encoded_config = get_raw_encoded_config(event)

    try:
        article = parse_article(raw_encoded_article)
        config = parse_config(raw_encoded_config, kms_client)
    except BadRequestError as e:
        logger.warning(f"Exception occurred: {e}")
        return create_failed_response(
            f"Bad Request: {e}", raw_encoded_article=raw_encoded_article
        )

    put_article(article, config, dynamodb_resource)
    return create_success_response(article)


def parse_article(encoded_article: str):
    try:
        raw_article = urlsafe_b64decode(encoded_article.encode()).decode()
        return Article.loads(raw_article)
    except Exception as e:
        logger.warning(f"Exception occurred: {e}")
        raise BadRequestError(str(e))


def parse_config(
    encoded_config: Optional[str], kms_client: BaseClient
) -> Optional[PostedConfig]:
    if encoded_config is None:
        return None
    option = {"CiphertextBlob": urlsafe_b64decode(encoded_config.encode())}
    resp = kms_client.decrypt(**option)
    raw_config = resp["Plaintext"].decode()
    try:
        return PostedConfig(raw_config)
    except Exception as e:
        logger.warning(f"Exception occurred: {e}")
        raise BadRequestError(str(e))


def put_article(
    article: Article, config: Optional[PostedConfig], dynamodb_resource: ServiceResource
):
    table = dynamodb_resource.Table(get_articles_table_name())
    item = {
        "userId": get_user_id(),
        "createdAt": int(datetime.now(timezone.utc).timestamp() * 1000),
        "url": article.url,
        "title": article.title,
    }
    if config is not None:
        item["tags"] = config.tags
    table.put_item(Item=item)
