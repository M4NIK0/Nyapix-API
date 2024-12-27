FROM python:3.12
RUN pip install pdm
WORKDIR /app
RUN apt-get update && apt-get install libgl1 ffmpeg -y
ADD  pyproject.toml .
RUN pdm install
COPY  ./src /app/src
COPY  ./assets /app/assets
CMD pdm run python src/main.py

LABEL maintainer="Maniko"
LABEL version="0.2"
LABEL description="NyaPix API Server"
