import json
from typing import Optional

from botocore.client import BaseClient
from requests_oauthlib import OAuth1Session

from tools.aws_tools import get_ssm_client


def main(event, arg_ssm_client: Optional[BaseClient] = None):
    ssm_client = get_ssm_client() if arg_ssm_client is None else arg_ssm_client
    message = create_message(event)
    tweet(message, ssm_client)


def get_twitter_certification(ssm_client: BaseClient) -> dict:
    option = {"Name": "TwitterCertification", "WithDecryption": True}
    resp = ssm_client.get_parameter(**option)
    return json.loads(resp["Parameter"]["Value"])


def create_message(event) -> str:
    item = event["Records"][0]["dynamodb"]["NewImage"]
    url = item["url"]["S"]
    title = item["title"]["S"]
    message = "\n".join([f"下記サイトをBookmarkしました。 #bookmarks", title, url])
    return message


def tweet(message: str, ssm_client: BaseClient):
    certification = get_twitter_certification(ssm_client)
    twitter = OAuth1Session(
        certification["ConsumerKey"],
        certification["ConsumerSecret"],
        certification["AccessToken"],
        certification["AccessTokenSecret"],
    )
    twitter.post(
        "https://api.twitter.com/1.1/statuses/update.json", params={"status": message}
    )
