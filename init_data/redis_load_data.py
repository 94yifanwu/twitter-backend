import sqlite3
from sqlite3 import Error
import json
import redis
import re
import sys


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def query(conn):
    cur = conn.cursor()
    cur.execute("SELECT id,text FROM posts")
    rows = cur.fetchall()
    return rows


r = redis.Redis()
database = "./init_data/timelines.db"
connection = create_connection(database)
posts = query(connection)
json_posts = {}
#STOP_WORDS = set('''the he at but there of was be not use and for this what an a on have all each to are from were which in as or we she is with ine when do you his had your how that they by can their it I word said if'''.split())
f = open("./50stopwords.txt", "r")
STOP_WORDS = f.read()
f.close()

for post in posts:  # post[0] is id and post[1] is text
    text = post[1].lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # QUERY_RE = re.compile("[+-]?[a-z']{2,}")
    words = text.split()
    for word in words:
        if(len(word) > 2):  # don't save 1 or 2 letters word
            if word not in STOP_WORDS:
                if word not in json_posts:
                    json_posts[word] = [str(post[0])]
                else:
                    json_posts[word].append(str(post[0]))
                r.sadd(word, str(post[0]))
print('- Search Table status: Loaded data to Redis')
