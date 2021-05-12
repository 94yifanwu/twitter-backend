# use this file and let worker to call it.
import logging.config
import bottle
import json
import requests
from bottle import get, post, error, abort, request, response, HTTPResponse, redirect, HTTPError
from rq import Queue
from redis import Redis


app = bottle.default_app()
app.config.load_config('./etc/gateway.ini')
logging.config.fileConfig(app.config['logging.config'])

logging.disable(logging.CRITICAL)  # use this to show logging.debug message

servers_list = json.loads(app.config['proxy.upstreams'])
redis_conn = Redis()
q1 = Queue('high', connection=redis_conn)
q2 = Queue('default', connection=redis_conn)
q3 = Queue('low', connection=redis_conn)


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
    inputs = q1.fetch_job(queue_id).result
    logging.debug(inputs)

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
