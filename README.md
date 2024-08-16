# Nyapix API

## Installation

### Requirements

#### Inside a Docker Container

- Clone/Download this repository
- Docker and Docker Compose

#### Without Docker

- Python 3.11 or higher
- [PDM](https://pdm-project.org/en/latest/)

### Install

#### Inside a Docker Container

1. Copy `.env.example` to `.env` and modify the values as needed.
2. Run the following command to start the application:

```bash
docker-compose up -d
```

3. Access the application at `http://<ip>:<port>/docs` via your browser or [API client](https://github.com/M4NIK0/Nyapix-client).
4. To stop the application, run the following command:

```bash
docker-compose down
```

#### Without Docker

1. Install the required dependencies:

```bash
pdm install
```

2. Copy `.env.example` to `.env` and modify the values as needed. (Please note that the API master key has access to all endpoints with all permissions. It is recommended to create a new API key with the necessary permissions once configured.)
3. Run the following command to start the application:

```bash
pdm run src/main.py
```

4. Access the application at `http://<ip>:<port>/docs` via your browser or [API client](https://github.com/M4NIK0/Nyapix-client).
5. To stop the application, press `Ctrl + C`.

## Development

This project uses [FastAPI](https://fastapi.tiangolo.com/), [uvicorn](https://www.uvicorn.org/), and [PDM](https://pdm-project.org/en/latest/).
