# infinitePlaylists

The process of discovering new playlists and/or artists on Spotify is far from perfect. There are a limited number of suggestions on their "Discover" and "Browse" pages, and a handful of recommended songs attached to each playlist. This project aims to make discovery easier.

The steps taken to create recommendations is as follows:

1. Develop a Python script for extracting playlist data from Spotify, transforming that data into a tabular format, and uploading the result to an AWS S3 bucket.
2. Write a Dockerfile to containerize the ETL script. An entrypoint should be used to pass Spotify playlist ids to the script.
3. Leverage Kubernetes to run several ETL containers in parallel, using a Redis-based work queue to process ~200,000 Spotify playlists.
4. Develop a seq2seq model in Pytorch or Keras that accepts a new playlist ID as input and recommends one of the ~200,000 playlists.
5. Host the model in a simple Flask app.

So far, steps 1-2 are complete; 3-4 are in progress.





