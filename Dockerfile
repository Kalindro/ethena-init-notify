FROM python:3.10

RUN pip install poetry

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

ENV PYTHONPATH=${PYTHONPATH}:${PWD} \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY poetry.lock pyproject.toml README.md /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root \
    && rm -rf $POETRY_CACHE_DIR

COPY . /app

ENTRYPOINT ["poetry", "run", "python", "-u", "src/main.py"]
