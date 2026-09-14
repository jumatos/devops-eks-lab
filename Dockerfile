FROM python:3.11-slim-trixie@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY app/requirements.txt /srv/requirements.txt

RUN python -m pip install --only-binary=:all: -r /srv/requirements.txt \
    && python -m pip uninstall -y setuptools wheel \
    && python -m pip check

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 \
        --gid appuser \
        --no-create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY app/ /srv/app/

USER 10001:10001

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]