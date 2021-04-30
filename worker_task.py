# use this file and let worker to call it.
import logging.config
import bottle
import json
import requests
import sys
from bottle import get, post, error, abort, request, response, HTTPResponse, redirect, HTTPError
from rq import Queue
from redis import Redis

app = bottle.default_app()
app.config.load_config('./etc/gateway.ini')
logging.config.fileConfig(app.config['logging.config'])

servers_list = json.loads(app.config['proxy.upstreams'])
redis_conn = Redis()
q = Queue(connection=redis_conn)


logging.disable(logging.CRITICAL)


def worker_post_a_twitter(inputs):
    logging.debug("in worker_post_a_twitter")
    server_posts = (servers_list['posts'][0])
    headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.request(
        method='POST',
        url=server_posts+'/posts/',
        data=inputs,
        headers=headers,
    )
    logging.debug('status code is: '+str(response.status_code))
    logging.debug((response.content))
    return response.content


def worker_inverted_index(queue_id):
    logging.debug("worker_inverted_index")
    inputs = q.fetch_job(queue_id).result

    server_search_engine = (servers_list['search-engine'][0])
    headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.request(
        method='POST',
        url=server_search_engine+'/search-engine/inverted-index/',
        data=inputs,
        headers=headers,
    )
    logging.debug('status code is: '+str(response.status_code))
    logging.debug((response.content))
