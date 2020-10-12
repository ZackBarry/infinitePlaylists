import sys
import time
import rediswq
from spotify_etl import Load

host = "redis"

q = rediswq.RedisWQ(name="job2", host=host)

print("Worker with sessionID: " + q.sessionID())

while not q.empty():
    item = q.lease(lease_secs=10, block=True, timeout=2)
    if item is not None:
        itemstr = item.decode("utf-8")
        print("Working on " + itemstr)
        load_obj = Load('playlist', playlist_id, aws_bucket)
        load_obj.load()
        q.complete(item)
    else:
        print("Waiting for work")
print("Queue empty, exiting")
