import sys
from datetime import datetime
from time import time
from spotify_etl import Load

# Example call: python run_etl.py infinite-playlists-test 42gxpKWSAzT5k05nIzP3O2


def main():
    script = sys.argv[0]
    aws_bucket = sys.argv[1]
    playlist_ids = sys.argv[2:]

    print('running %s to extract playlist data to %s AWS S3 bucket' % (script, aws_bucket))
    print('playlist ids:')
    for p_id in playlist_ids:
        print(p_id)

    print('job start: %s' % datetime.now())
    start_sec = int(time())

    load_obj = Load('playlist', playlist_ids, aws_bucket)
    load_obj.load()

    end_sec = int(time())
    print('job end: %s' % datetime.now())
    print('seconds elapsed: %i' % (end_sec - start_sec))


if __name__ == '__main__':
    main()
