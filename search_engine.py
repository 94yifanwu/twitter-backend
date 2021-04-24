#
# Simple API gateway in Python
#
# Inspired by <https://github.com/vishnuvardhan-kumar/loadbalancer.py>
#
# in this project, database_name is to indicate the url path element.
# for example, localhost:5100/users/users.json , users is database and users.json is table/query

import sys
import json
import http.client
import logging.config
import itertools
import base64
import bottle
from bottle import auth_basic, route, request, response, get
from bottle.ext import redis

import requests


# Allow JSON values to be loaded from app.config[key]
#
def json_config(key):
    value = app.config[key]
    return json.loads(value)


# Set up app and logging
#
app = bottle.default_app()
app.config.load_config("./etc/gateway.ini")

logging.config.fileConfig(app.config["logging.config"])

plugin = bottle.ext.redis.RedisPlugin(host='localhost')
app.install(plugin)


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


@get('/')
def aaa():
    return 'use /search/<item> in url'


@app.route('/search/<item>')
def show(item, rdb):
    return 'this /search/<item>'

    return item
    row = rdb.get(item)
    if row:
        return template('showitem', item=item)
    return HTTPError(404, "Page not found")
