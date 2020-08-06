FROM python:3.7.8-slim-buster
RUN apt-get update && \
    apt-get -y install gcc
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY run_etl.py /app
COPY spotify_etl.py /app
COPY config.py /app
ENTRYPOINT ["python", "run_etl.py"]