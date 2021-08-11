FROM python:3.12.3-bookworm

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y curl

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

CMD ["python", "haiku.py"]
