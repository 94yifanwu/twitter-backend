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


# Simplify DB access
#
# Adapted from
# <https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#easy-querying>
#
def query(db, sql, args=(), one=False):
    cur = db.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row))
          for row in cur.fetchall()]
    cur.close()

    return (rv[0] if rv else None) if one else rv


def execute(db, sql, args=()):
    cur = db.execute(sql, args)
    id = cur.lastrowid
    cur.close()

    return id


# initializing punctuations string
# punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
# Removing punctuations in string
# Using loop + punctuation string
'''
for s in test_str: 
    if s in punc: 
        test_str = test_str.replace(s, "") 
'''


@get('/search-engine/<item>')
def show_first_page(item, rdb):
    row = rdb.get(item)
    if row:
        return (row)
    return HTTPError(404, item+"  hehehe Page not found")


# return all result OR
# test: http://localhost:5000/search-engine/search/sets+yifan
@get('/search-engine/search/<inputs>')
def search_keys(inputs, rdb):
    keys = inputs.split('+')  # the input is splited by + sign
    post_ids = []
    for key in keys:
        row = rdb.smembers(key)
        if row:
            for r in row:
                post_ids.append(r.decode('UTF-8'))
        else:
            pass
    return str(post_ids)  # convert to json?


f = open("./stopwords.txt", "r")
STOP_WORDS = f.read()
f.close()


@post('/search-engine/inverted_index/')
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
                print('sadd '+word+' '+post_id)
                rdb.sadd(word, post_id)


#STOP_WORDS = set('''the at but there of was be not use and for this what an a on have all each to are from were which in as or we she is with ine when do you his had your how that they by can their it I word said if'''.split())
'''
WORDS_RE = re.compile("[a-z']{2,}")
def tokenize(content):
    words = set()
    for match in WORDS_RE.finditer(content.lower()):
        word = match.group().strip("'")
        if len(word) >= 2:
            words.add(word)
    return words - STOP_WORDS


def index_document(conn, docid, content):
    words = tokenize(content)
    pipeline = conn.pipeline(True)
    for word in words:
        pipeline.sadd('idx:' + word, docid)
    return len(pipeline.execute())


def _set_common(conn, method, names, ttl=30, execute=True):
    id = str(uuid.uuid4())
    pipeline = conn.pipeline(True) if execute else conn
    names = ['idx:' + name for name in names]
    getattr(pipeline, method)('idx:' + id, *names)
    pipeline.expire('idx:' + id, ttl)
    if execute:
        pipeline.execute()
    return id


def intersect(conn, items, ttl=30, _execute=True):
    return _set_common(conn, 'sinterstore', items, ttl, _execute)


def union(conn, items, ttl=30, _execute=True):
    return _set_common(conn, 'sunionstore', items, ttl, _execute)


def difference(conn, items, ttl=30, _execute=True):
    return _set_common(conn, 'sdiffstore', items, ttl, _execute)


QUERY_RE = re.compile("[+-]?[a-z']{2,}")


def parse(query):
    unwanted = set()
    all = []
    current = set()
    for match in QUERY_RE.finditer(query.lower()):
        word = match.group()
        prefix = word[:1]
        if prefix in '+-':
            word = word[1:]
        else:
            prefix = None
        word = word.strip("'")
        if len(word) < 2 or word in STOP_WORDS:
            continue
        if prefix == '-':
            unwanted.add(word)
            continue
        if current and not prefix:
            all.append(list(current))
            current = set()
        current.add(word)
    if current:
        all.append(list(current))
    return all, list(unwanted)
'''
