from logger.my_logger import MyLogger
from tools.aws_tools import save_lambda_request_id

from .show import main

logger = MyLogger(__name__)


@save_lambda_request_id()
def handler(event, context):
    try:
        return main(event)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return {
            "statusCode": 500,
            "header": {"Content-Type": "plain/html"},
            "body": create_failed_process_page(),
        }


def create_failed_process_page():
    return """
<!DOCTYPE html>
<html lang="ja-jp">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width" />
  <title>Failed Process Result Page</title>
</head>
<body>
  <h2> Internal Server Error</h2>
</body>
</html>
"""
