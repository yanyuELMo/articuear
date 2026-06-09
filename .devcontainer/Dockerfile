FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/silentspeechoe

COPY .devcontainer/requirements.txt ./requirements.txt
COPY .devcontainer/requirements-dev.txt ./requirements-dev.txt
COPY pyproject.toml README.md ./

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements-dev.txt
