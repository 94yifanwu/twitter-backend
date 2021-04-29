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


def get_user_id(username):
    response = gateway("users/users.json?username=" +
                       username + "&_shape=array&_nl=on")
    response = json.loads(response)
    user_id = response["id"]
    return user_id


def get_username(user_id):
    response = gateway("users/users.json?id=" +
                       user_id + "&_shape=array&_nl=on")
    response = json.loads(response)
    return response["username"]


def get_following(username):
    response = gateway("users/following.json?username=" +
                       username + "&_shape=array")
    response = json.loads(response)
    following_array = []
    for res in response:
        following_array.append(res["friendname"])
    return following_array


def get_posts(username):
    response = gateway("timelines/posts.json?username=" +
                       username + "&_shape=array")
    response = json.loads(response)
    posts_array = []
    for res in response:
        posts_array.append(res["text"])
    return posts_array


def send_400(url_array):
    response.status = 400
    return response


def send_401():
    response.status = 401
    response.body = {"error: No Permission to see this user"}
    return response


def is_authenticated_user(username, password):

    query = (
        "/users/users.json?username="
        + username
        + "&password="
        + password
        + "&_shape=array&_nl=on"
    )
    server = json_config("proxy.upstreams")["users/*"]
    query = server[0] + query
    response = requests.get(query)
    if len(response.content) > 0:
        return True
    return False


@get("/home/<username>")
@auth_basic(is_authenticated_user, realm="private", text="Unauthorized")
def get_feed(username):
    username_auth = (request.auth)[0]
    if username != username_auth:  # can't see other people's home feed
        return send_401()

    # 1. get following friends
    friends_username = get_following(username)
    # 2. get posts from each friend
    friends_posts = []
    for friend_username in friends_username:
        friend_posts = get_posts(friend_username)
        for friend_post in friend_posts:
            friends_posts.append(friend_post)
    return friends_posts


@route("<url:re:.*>", method="ANY")
@auth_basic(is_authenticated_user, realm="private", text="Unauthorized")
def gateway(url):
    path = request.urlparts._replace(scheme="", netloc="").geturl()
    # remove the first char of 'url', if it's '/'
    if "?" in path:
        url = path
    if url[0] == "/":
        url = url[1:]

    url_array = url.split("/")
    database_name = url_array[0]

    # logging.debug('url is: '+url)
    # logging.debug('path is: '+path)
    # logging.debug("url_array is: " + str(url_array))
    # sys.exit()

    if ".json" in url:
        database_name += "/*"

    # load balancing
    # if it's False then LB_table won't remove bad server
    turn_on_LB_table_remove = False

    global LB_table
    try:
        if LB_table:
            pass
        # logging.debug("LB_table is: \n" + str(LB_table).replace(",", "\n"))
    except NameError:
        LB_table = json_config("proxy.upstreams")

    upstream_servers = LB_table[database_name]

    if len(upstream_servers) > 1:
        global LB_table_iter
        try:
            upstream_server = next(LB_table_iter)
        except:
            LB_table_iter = itertools.cycle(upstream_servers)
            upstream_server = next(LB_table_iter)
    else:
        # for single copy server
        if len(upstream_servers) > 0:
            upstream_server = upstream_servers[0]
        else:
            response.status = 503
            return response

    upstream_url = upstream_server + "/" + url

    #logging.debug("Upstream URL: %s", upstream_url)

    headers = {}
    for name, value in request.headers.items():
        if name.casefold() == "content-length" and not value:
            headers["Content-Length"] = "0"
        else:
            headers[name] = value

    try:
        headers["Content-Type"] = "application/json; charset=utf-8"
        upstream_response = requests.request(
            request.method,
            upstream_url,
            data=request.body,
            headers=headers,
            cookies=request.cookies,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        # logging.exception(e)
        response.status = 503
        return {
            "method": e.request.method,
            "url": e.request.url,
            "exception": type(e).__name__,
        }

    response.status = upstream_response.status_code
    status_code = upstream_response.status_code

    # remove this, just to test
    # status_code = 500

    # remove bad server from load balancer
    if status_code == 500:
        # logging.debug("before remove, LB_table are:\n "+ str(LB_table).replace(',','\n'))
        # logging.debug("removeing: "+ database_name + ' : ' + upstream_server)
        # turn on or off LB-remove
        if (turn_on_LB_table_remove == True):
            LB_table[database_name].remove(upstream_server)
        LB_table_iter = itertools.cycle(LB_table[database_name])
        # logging.debug("after remove, LB_table are: \n"+ str(LB_table).replace(',','\n'))

        # if no server in the LB_table_iter, return 503
        if len(upstream_servers) == 0:
            response.status = 503
            upstream_response.status = 503
            return {"error": "no server availale in LB_table"}

    for name, value in upstream_response.headers.items():
        if name.casefold() == "transfer-encoding":
            continue
        response.set_header(name, value)

    return upstream_response.content


@get("/favicon.ico")
def fav():
    return 'fav'
