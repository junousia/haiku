FROM python:3.9.6-buster

COPY . /app
WORKDIR /app
RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y python3-dev libffi-dev gcc musl-dev libvoikko1 voikko-fi python3-libvoikko
RUN pip install -r requirements.txt
RUN cp /usr/lib/python3/dist-packages/libvoikko.py /app/libvoikko.py
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

EXPOSE 5000

CMD ["python", "haiku.py"]

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
