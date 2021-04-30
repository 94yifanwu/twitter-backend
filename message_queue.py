from rq import Queue, use_connection
from redis import Redis
from task import add
import time
import logging

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
