# Nyapix API

## Installation

### Requirements

#### Inside a Docker Container

- Clone/Download this repository
- Docker and Docker Compose

#### Without Docker

- Python 3.12 or higher
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

## API Documentation

API documentation is available at `http://<ip>:<port>/docs` when running and configured.

### Authentication

The API uses an API key for authentication. The API key is passed as a header as `api_key` parameter.

### Endpoints

#### \/

| Method | Endpoint       | Description                                                                       |
|--------|----------------|-----------------------------------------------------------------------------------|
| GET    | nyapix_version | Returns the API version.                                                          |
| GET    | ping           | Returns a succesful response if API key is valid and the API is running properly. |

#### \/admin/ - Administration endpoints

| Method | Endpoint | Description                                                                                   |
|--------|----------|-----------------------------------------------------------------------------------------------|
| GET    | setup    | Sets up the database and creates the necessary tables if they do not exist. (Master key only) | 

#### \/tag/ - Tag management endpoints

| Method | Endpoint | Description                          |
|--------|----------|--------------------------------------|
| POST   | add      | Adds a new tag if it does not exist. |
| POST   | remove   | Remove a tag if it exists.           |
| POST   | edit     | Edit a tag if it exists.             |
| GET    | list     | Get all tags.                        |

#### \/item/ - Item management endpoints

| Method | Endpoint     | Description                                            |
|--------|--------------|--------------------------------------------------------|
| POST   | add          | Adds a new item.                                       |
| POST   | remove       | Remove an item.                                        |
| POST   | edit         | Edit an item.                                          |
| POST   | purge_nofile | Remove all items that do not have a file. (admin only) |

#### \/content/ - Content search and download endpoints

| Method | Endpoint              | Description                     |
|--------|-----------------------|---------------------------------|
| GET    | search                | Search for items based on tags. |
| GET    | [content id]/info     | Get information about an item.  |
| GET    | [content id]/thumb    | Get the thumbnail of an item.   |
| GET    | [content id]/download | Download an item.               |

#### \/statistics/ - Statistics endpoints

| Method | Endpoint | Description              |
|--------|----------|--------------------------|
| GET    | current  | Get current statistics.  |
| GET    | all-time | Get all-time statistics. |

#### \/user - User management endpoints

| Method | Endpoint | Description                                                     |
|--------|----------|-----------------------------------------------------------------|
| POST   | add      | Add a new user (admin only), returns user's token               |
| POST   | remove   | Remove a user (admin only)                                      |
| POST   | info     | Get a user's permission (admin only), return user's permissions |
| POST   | edit     | Edit a user's permission (admin only)                           |

## Development

This project uses [FastAPI](https://fastapi.tiangolo.com/), [uvicorn](https://www.uvicorn.org/), and [PDM](https://pdm-project.org/en/latest/).
