FROM python:3.9-slim

RUN pip install jupyter \ 
    requests

WORKDIR /workspace