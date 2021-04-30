from rq import Queue, use_connection
from redis import Redis
from task import add
import time
import logging


import sys
import logging.config
import bottle
import textwrap
import re
import json
from bottle import get, post, error, abort, request, response, HTTPResponse, redirect, HTTPError
from bottle.ext import redis


# Set up app, plugins, and logging
#
app = bottle.default_app()
app.config.load_config('./etc/conf.ini')
plugin = bottle.ext.redis.RedisPlugin(host='localhost')
app.install(plugin)
logging.config.fileConfig(app.config['logging.config'])


def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


app.default_error_handler = json_error_handler
if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)


@post('/message-queue/post_a_twitter')
def post_a_twitter(rdb):

    inputs = (request.json)
    print(inputs['text'])
    return 'hello'


# use redis by default
# create work queue
redis_conn = Redis()
q = Queue(connection=redis_conn)

# notice: cann't run a task function in __main__ module
# because rq save module and function name in redis
# when rqworker running, __main__ is another module
# enqueue tasks,function enqueue returns the job instance
job = q.enqueue(add, 3, 9)
job = q.enqueue(add, 4, 9)
job = q.enqueue(add, 5, 9)
job = q.enqueue(add, 6, 9)

time.sleep(3)
# get the job result by job.result
print("result is %s", job.result)
