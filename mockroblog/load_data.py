from decimal import Decimal
import json
import boto3


def load_data(chats, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")

    table = dynamodb.Table("messages")
    for chat in chats:
        chat_id = chat["chat_id"]
        timestamp = chat["timestamp"]
        print("- Adding chat:", chat_id, timestamp)
        table.put_item(Item=chat)


if __name__ == "__main__":
    with open("./mockroblog/chat_data.json") as json_file:
        chat_list = json.load(json_file)
    load_data(chat_list)
