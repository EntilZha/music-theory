FROM python:3.10

RUN pip install poetry==1.1.13

RUN mkdir -p /code/music-theory
WORKDIR /code/music-theory
COPY pyproject.toml poetry.lock /code/music-theory/
RUN poetry export --without-hashes -f requirements.txt > reqs.txt && pip install -r reqs.txt

COPY . /code/music-theory
EXPOSE 8501

CMD ["streamlit", "run", "--server.address", "0.0.0.0", "app.py"]