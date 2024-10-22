FROM python:3.12

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install

COPY app ./app

CMD ["poetry", "run", "python", "-m", "app.bot"]
