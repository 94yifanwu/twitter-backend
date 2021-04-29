import sys
import textwrap
import logging.config
import bottle
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

f = open("./stopwords.txt", "r")
STOP_WORDS = f.read()
f.close()

# Return errors in JSON
#
# Adapted from # <https://stackoverflow.com/a/39818780>
#


def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


app.default_error_handler = json_error_handler

# Disable warnings produced by Bottle 0.12.19.
#
#  1. Deprecation warnings for bottle_sqlite
#  2. Resource warnings when reloader=True
#
# See
#  <https://docs.python.org/3/library/warnings.html#overriding-the-default-filter>
#
if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)


# AND operation
@get('/search-engine/search-all/<inputs>')
def search_keys_AND(inputs, rdb):
    all_json = search_keys_json_format(inputs, rdb)

    values_all_json_array = all_json.values()
    values_duplicate = []

    for values in values_all_json_array:
        for value in values:
            values_duplicate.append(value)

    values_AND_result = set()
    values_not_duplicate = set()
    for value in values_duplicate:
        if value not in values_not_duplicate:
            values_not_duplicate.add(value)
        else:
            values_AND_result.add(value)

    return json.dumps(list(values_AND_result))


# OR operation
@get('/search-engine/search-any/<inputs>')
def search_keys_OR(inputs, rdb):
    all_json = search_keys_json_format(inputs, rdb)
    post_id_set = set()
    for key in all_json:
        for value in all_json[key]:
            post_id_set.add(value)
    return json.dumps(list(post_id_set))

# Exclude operation


@get('/search-engine/search-exclude/<includeList>/<excludeList>')
def search_keys_EXCLUDE(includeList, excludeList, rdb):
    include_keys_values = search_keys_json_format(includeList, rdb)
    exclude_keys_values = search_keys_json_format(excludeList, rdb)
    print(include_keys_values)
    print(exclude_keys_values)
    include_values = set()
    exclude_values = set()

    for values in exclude_keys_values.values():
        for value in values:
            exclude_values.add(value)
    for values in include_keys_values.values():
        for value in values:
            if value not in exclude_values:
                include_values.add(value)

    return json.dumps(list(include_values))


# return all and return result by key-value format
# @get('/search-engine/search/<inputs>')  # delete this line later
def search_keys_json_format(inputs, rdb):
    keys = inputs.split('+')  # the input is splited by + sign
    post_ids = {}
    for key in keys:
        row = rdb.smembers(key)
        if row:
            for r in row:
                # post_ids.append(r.decode('UTF-8'))
                try:
                    post_ids[key].append(r.decode('UTF-8'))
                except:
                    post_ids[key] = [r.decode('UTF-8')]
        else:
            pass
    return post_ids  # convert to json?


@post('/search-engine/inverted-index/')
def inverted_index(rdb):
    # get inputs
    inputs = request.json
    post_id = inputs['post_id']
    text = inputs['text'].lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()

    # sadd to redis - word:post_id
    for word in words:
        print('sadd '+word+' '+post_id)
        if(len(word) > 2):  # don't save 1 or 2 letters word
            if word not in STOP_WORDS:
                rdb.sadd(word, post_id)

    return {"post_id": post_id, "text": text}
