FROM python:3.7.8-slim-buster

WORKDIR /app

RUN apt-get update \
    && apt-get install -y gcc=8.3.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app

RUN pip install \
    --upgrade \
    --no-deps \
    --requirement requirements.txt

COPY spotify_etl/* ./

CMD ["python", "run_etl.py"]
