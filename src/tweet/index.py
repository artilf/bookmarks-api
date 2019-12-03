from client import main
from logger.my_logger import MyLogger
from tools.aws_tools import save_lambda_request_id

logger = MyLogger(__name__)


@save_lambda_request_id()
def handler(event, context):
    try:
        main(event)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        raise
