import json
from decimal import Decimal


def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(event, default=default)
    }


def default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if int(obj) == obj else float(obj)
    try:
        return str(obj)
    except Exception:
        return None