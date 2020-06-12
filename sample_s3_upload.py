# https://stackoverflow.com/a/56275519/11407644

import pandas as pd
import boto3
import sf3s
# sf3s must be installed (pandas uses it behind the scenes for S3 connections)
# AWS authentication credentials should be set up: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

s3 = boto3.client('s3')

df = pd.DataFrame( [ [1, 1, 1], [2, 2, 2] ], columns=['a', 'b', 'c'])

df.to_csv('s3://infinite-playlists/test/dummy.csv', index=False)

