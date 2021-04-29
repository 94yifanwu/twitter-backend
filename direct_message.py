# Science Fiction Novel API - Bottle Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

import sys
import textwrap
import logging.config
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import bottle
from bottle import get, post, error, abort, request, response, HTTPResponse
from botocore.exceptions import ClientError
import uuid
import datetime


# Allow JSON values to be loaded from app.config[key]
#
def json_config(key):
    value = app.config[key]
    return json.loads(value)


# Set up app and logging
#
app = bottle.default_app()
app.config.load_config("./etc/conf.ini")

logging.config.fileConfig(app.config["logging.config"])


# If you want to see traffic being sent from and received by calls to
# the Requests library, add the following to etc/gateway.ini:
#
#   [logging]
#   requests = true
#
if json_config("logging.requests"):
    http.client.HTTPConnection.debuglevel = 1

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    logging.debug("Requests logging enabled")


# Return errors in JSON
#
# Adapted from <https://stackoverflow.com/a/39818780>
#
def json_error_handler(res):
    if res.content_type == "application/json":
        return res.body
    res.content_type = "application/json"
    if res.body == "Unknown Error.":
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({"error": res.body})


app.default_error_handler = json_error_handler


# Disable warnings produced by Bottle 0.12.19 when reloader=True
#
# See
#  <https://docs.python.org/3/library/warnings.html#overriding-the-default-filter>
#
if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore", ResourceWarning)

# Routes


messages_table = boto3.resource("dynamodb", endpoint_url="http://localhost:8000").Table(
    "messages"
)

# def send_direct_message(receiver, sender, content, quick_replies=None):


def send_direct_message(inputs):
    chat_id = str(uuid.uuid4())
    chat_id = inputs["sender"] + "#" + chat_id[:4]
    Items = {}
    if "quick_replies" in inputs:
        Items["quick_replies"] = inputs["quick_replies"]
    if "sender" in inputs:
        Items["sender"] = inputs["sender"]
    if "receiver" in inputs:
        Items["receiver"] = inputs["receiver"]
    if "content" in inputs:
        Items["text"] = inputs["content"]
    Items["chat_id"] = chat_id
    Items["timestamp"] = str(datetime.datetime.now())
    response = messages_table.put_item(Item=Items)

    return {"New chat created": Items}


# def reply_to_direct_message(chat_id, receiver, sender, is_text, content):
def reply_to_direct_message(inputs):

    receiver = inputs["receiver"]
    chat_id = inputs["chat_id"]

    last_message_response = messages_table.query(
        KeyConditionExpression=Key("chat_id").eq(chat_id),
        FilterExpression=Attr("sender").eq(receiver),
        ScanIndexForward=False,  # order_by
    )

    # return json.dumps(last_message_response)

    Items = {}
    if inputs["is_text"] == "False":
        Items["quick_reply"] = inputs["content"]
        try:
            Items["text"] = last_message_response["Items"][0]["quick_replies"][inputs["content"]]
        except:
            abort(400, 'can not use quick_reply')
    elif inputs["is_text"] == "True":
        Items["text"] = inputs["content"]
    if "sender" in inputs:
        Items["sender"] = inputs["sender"]
    if "receiver" in inputs:
        Items["receiver"] = inputs["receiver"]
    Items["chat_id"] = chat_id
    Items["timestamp"] = str(datetime.datetime.now())
    response = messages_table.put_item(Item=Items)
    return {"Reply": Items}


@post("/dm/")
def DM(dynamodb=None):
    inputs = request.json
    if not inputs:
        abort(400)

    try:
        username_auth = (request.auth)[0]
        if username_auth != inputs["sender"]:
            #response.status = 401
            return {"Unauthorized": "Not signed in with the sender"}
    except:
        logging.debug("no request.auth")

    if "chat_id" in inputs:
        return reply_to_direct_message(inputs)
    else:  # create a new chat
        return send_direct_message(inputs)


@get("/dm/username/<username>/message/<message_id>")
def DM_get_messages(username, message_id=None):

    try:
        username_auth = (request.auth)[0]
        if username_auth != username:
            #response.status = 401
            return {"Unauthorized": "Not signed in with the sender"}
    except:
        logging.debug("no request.auth")

    chat_id = username + "#" + message_id
    try:
        if message_id != None:
            response = messages_table.query(
                KeyConditionExpression="chat_id = :chat_id",
                ExpressionAttributeValues={
                    ":chat_id": chat_id,
                },
            )
    except ClientError as e:
        return e.response
    else:
        return json.dumps(response["Items"])


@get("/dm/username/<username>/receiver")
def list_direct_messages_for(username):
    try:
        username_auth = (request.auth)[0]
        if username_auth != username:
            return {"Unauthorized": "Not signed in with the sender"}
    except:
        logging.debug("no request.auth")
        #abort(401, "Not signed in with the sender")

    response = messages_table.query(
        IndexName="receiver-index",
        KeyConditionExpression=Key("receiver").eq(username),
    )
    return json.dumps(response["Items"])
