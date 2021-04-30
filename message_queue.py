from worker_task import worker_post_a_twitter, worker_inverted_index
#from search_engine import inverted_index
from rq import Queue, use_connection
from redis import Redis
import sys
import logging.config
import bottle
import json
import requests
from bottle import get, post, error, abort, request, response, HTTPResponse, redirect, HTTPError
from bottle.ext import redis
import time

app = bottle.default_app()
app.config.load_config('./etc/conf.ini')
plugin = bottle.ext.redis.RedisPlugin(host='localhost')
app.install(plugin)
logging.config.fileConfig(app.config['logging.config'])
redis_conn = Redis()
q = Queue(connection=redis_conn)


@post('/message-queue/post-a-twitter')
def post_a_twitter(rdb):
    inputs = request.body
    job = q.enqueue(worker_post_a_twitter, inputs)
    # after get result
    time.sleep(3)
    new_post = (job.result).decode('UTF-8')
    print(new_post)
    # dependent to post_id
    if 'post_id' in new_post:
        job = q.enqueue(worker_inverted_index, job.result)
    response.status = 202
    # response.body = "Accepted, submitting to timelines service"
    # return response.content
    return {"Accepted": "submitting to timelines service"}
