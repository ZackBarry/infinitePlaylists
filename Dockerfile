FROM python:3.7.8-slim-buster
RUN apt-get update && \
    apt-get -y install gcc
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY spotify_etl/* /app
ENTRYPOINT ["python", "run_etl.py"]