import sys
import os
import time
import rediswq
from spotify_etl import Load

aws_bucket = os.environ.get('AWS_BUCKET', 'test-infinite-playlists')
print("Writing to: " + aws_bucket)

host = "redis"

q = rediswq.RedisWQ(name="job2", host=host)

print("Worker with sessionID: " + q.sessionID())
# want ~100 ids for ~40mb files
while not q.empty():
    items = [q.lease(lease_secs=2*40, block=True, timeout=2) for i in range(0, 2)]
    if items is not None:
        itemstrs = [item.decode("utf-8") for item in items]
        [print("Working on " + itemstr) for itemstr in itemstrs]
        load_obj = Load('playlist', itemstrs, aws_bucket, q.sessionID())
        load_obj.load()
        [q.complete(item) for item in items]
    else:
        print("Waiting for work")
print("Queue empty, exiting")
