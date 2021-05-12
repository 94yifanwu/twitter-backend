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
q1 = Queue('high', connection=redis_conn)
q2 = Queue('default', connection=redis_conn)
q3 = Queue('low', is_async=False, connection=redis_conn)


@post('/message-queue/post-a-twitter')
def post_a_twitter(rdb):
    inputs = request.body

    job_post = q1.enqueue(worker_post_a_twitter, inputs)  # return post_id

    # the inverted_index part is not ready yet .
    job_index = q3.enqueue(worker_inverted_index, job_post.id)

    response.status = 202
    return {"Accepted": "submitting to timelines service"}
