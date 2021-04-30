import logging.config
import bottle
import json
import requests
from bottle import get, post, error, abort, request, response, HTTPResponse, redirect, HTTPError


app = bottle.default_app()
app.config.load_config('./etc/conf.ini')
logging.config.fileConfig(app.config['logging.config'])


def worker_post_a_twitter(inputs):

    headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.request(
        method='POST',
        url='http://localhost:5200/posts/',
        data=inputs,
        headers=headers,
    )
    logging.debug('status code is: '+str(response.status_code))
