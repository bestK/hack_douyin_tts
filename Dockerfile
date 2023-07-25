FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && \
    apt-get install python3-pip build-essential -y && \
    rm -rf /var/lib/apt/lists/* 

COPY . .

RUN cd /app && \
    pip install -r requirements.txt

EXPOSE 443    

CMD uvicorn src.main:app --host 0.0.0.0 --port 443