import gzip
import json
from base64 import urlsafe_b64encode
from typing import Optional

from botocore.client import BaseClient

from logger.my_logger import MyLogger
from models.posted_config import PostedConfig
from tools.api_gw import create_response
from tools.auth import can_access
from tools.aws_tools import get_kms_client, get_ssm_client
from tools.environment_values import get_kms_key_id

logger = MyLogger(__name__)


class BadRequestError(Exception):
    pass


def main(
    event,
    arg_ssm_client: Optional[BaseClient] = None,
    arg_kms_client: Optional[BaseClient] = None,
):
    logger.info("event", event=event)
    ssm_client: BaseClient = get_ssm_client() if arg_ssm_client is None else arg_ssm_client
    kms_client: BaseClient = get_kms_client() if arg_kms_client is None else arg_kms_client
    if not can_access(event, ssm_client, is_header=True):
        return create_response(403, {"message": "Forbidden"})
    try:
        tags = get_tags(event)
        config = get_config(tags)
    except BadRequestError as e:
        return create_response(400, {"message": f"Bad Request: {e}"})

    encrypted_text = encrypt_config(config, kms_client)
    response = {"rawConfig": config, "encryptedConfig": encrypted_text}
    return create_response(200, response)


def get_tags(event):
    raw = event["body"]
    try:
        data = json.loads(raw)
        return data["tags"]
    except json.JSONDecodeError as e:
        logger.warning(f"Exception occurred: {e}")
        raise BadRequestError("Request Body is not json.")
    except KeyError as e:
        logger.warning(f"Exception occurred: {e}")
        raise BadRequestError("tags do not exist in request body.")


def get_config(tags) -> PostedConfig:
    try:
        return PostedConfig(tags=tags)
    except Exception as e:
        logger.warning(f"Exception occurred: {e}")
        raise BadRequestError(str(e))


def encrypt_config(config: PostedConfig, kms_client: BaseClient) -> str:
    data = config.to_json()
    option = {"KeyId": get_kms_key_id(), "Plaintext": gzip.compress(data.encode())}

    resp = kms_client.encrypt(**option)

    encoded = urlsafe_b64encode(resp["CiphertextBlob"])
    return encoded.decode()
