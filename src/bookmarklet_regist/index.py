from logger.my_logger import MyLogger
from tools.aws_tools import save_lambda_request_id

from .register import create_failed_response, main

logger = MyLogger(__name__)


@save_lambda_request_id()
def handler(event, context):
    try:
        return main(event)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return create_failed_response("InternalServerError")
