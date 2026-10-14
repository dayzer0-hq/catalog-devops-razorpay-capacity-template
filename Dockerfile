FROM python:3.12-slim

COPY app/ /srv/app/
WORKDIR /srv

ENV MODE=steady
ENV BATCH_MB=64
CMD ["python3", "app/worker.py"]
