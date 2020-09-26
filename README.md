# infinitePlaylists

The process of discovering new playlists and/or artists on Spotify is far from perfect. There are a limited number of suggestions on their "Discover" and "Browse" pages, and there are only a handful of recommended songs attached to each playlist. This project aims to make discovery easier.

The steps I'm taking to create recommendations is as follows:

1. Develop a Python script for extracting playlist data from Spotify, transforming that data into a tabular format, and uploading the result to an AWS S3 bucket.
2. Write a Dockerfile to containerize the ETL script. An entrypoint should be used to pass Spotify playlist ids to the script.
3. Leverage Kubernetes to run several ETL containers in parallel, using a Redis-based work queue to process ~200,000 Spotify playlists.
4. Develop a seq2seq model in Pytorch or Keras that accepts a new playlist ID as input and recommends one of the ~200,000 playlists.
5. Host the model in a simple Flask app.

So far, steps 1-2 are complete; 3-4 are in progress.
### Getting Started
---

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

#### Prerequisites

To run this code, you will need [Docker Desktop for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac) and [AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for writing to S3. AWS offers a [free-tier account](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc) that will be sufficient for running the example below.

Your AWS credentials should be stored at `$HOME/.aws/credentials`. They will not be baked in to the Docker image, they will be attached at run time via docker-compose.

#### Loading Playlist Data to S3

To load a list of playlists to an S3 bucket, start by identifying the playlist IDs (note that the playlists must be public). In the web-based Spotify playlist urls take the form `open.spotify.com/playlist/<playlist_id>`. For example, [Celtic Relaxation Music](https://open.spotify.com/playlist/42gxpKWSAzT5k05nIzP3O2) has playlist ID `42gxpKWSAzT5k05nIzP3O2`. It is not necessary to create an S3 bucket in advance; a bucket will be created with the name you provide if it does not already exist.

The following commands will create an image `infinite-playlists:<your_tag>`, spin up a docker-compose stack with AWS credentials attached, open a shell on the running container, and submit the Celtic Relaxation Music playlist for extraction to a bucket named `infinite-playlists-test`.  
```
$ make build IMAGE_TAG=<your_tag>
$ make debug IMAGE_TAG=<your_tag>
root@<container_id>:/app# python run_etl infinite-playlists-test 42gxpKWSAzT5k05nIzP3O2
```
