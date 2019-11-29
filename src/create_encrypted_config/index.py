from encrypter import main
from logger.my_logger import MyLogger
from tools.api_gw import create_response
from tools.aws_tools import save_lambda_request_id

logger = MyLogger(__name__)


@save_lambda_request_id()
def handler(event, context):
    try:
        return main(event)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return create_response(500, {"message": "InternalServerError"})
