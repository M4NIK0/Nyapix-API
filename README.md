# Nyapix API

### NOW WITH CLI CLIENT!

This project is made to store, sort and tag content according to your needs.
This tagging system permits to search for content with those parameters:
- Tags (General info about the content)
- Characters (Who is inside the content)
- Authors (Who created this content)
- Source (where does this content come from)

## Dependencies

- ffmpeg (image/video compression and conversion)
- docker (project deployment)
- python (api/backend)
- uvicorn + fastapi (api/backend)
- vuejs (frontend)
- postgresql (database)

## Setup

### Step 1

Setup .env for project & frontend

```bash
cp .env.example .env

cp Front/.env.example Front/.env
```

> #### DO NOT FORGET TO SET YOUR OWN PASSWORDS AND SECRETS IN THE .ENV FILES

#### Database environment variables
- `POSTGRES_USER`: Username for the database (default: postgres)
- `POSTGRES_PASSWORD`: Database password (default: postgres)
- `POSTGRES_DB`: Database name (default: postgres)
- `POSTGRES_HOST`: Database hostname (default: db)
- `POSTGRES_PORT`: Database access port (default: 5432)

#### Backend environment variables
- `API_PORT`: API access port (default: 5000)
- `API_HOST`: API hostname (default: backend)
- `JWT_SECRET`: JWT secret key (default: secret)
- `IS_HTTPS`: Set if the API is running on HTTPS (default: false)
- `ALLOW_REGISTER`: Set to allow user registration
- `DISABLE_SWAGGER`: Set to disable swagger documentation

#### Frontend environment variables (broken)
- `FRONT_PORT`: Frontend access port (default: 8081)

### Step 2

Start docker compose of the project

```bash
docker compose up --build
```

> Since it is your first startup, the backend will generate an admin account for you to use to finish the whole setup from the frontend, do not forget to change the password after the setup is complete and all tests have been conducted properly.

### Step 3

Login to the admin account on the website, change its password and username (it will be more secure)

### Step 4 (optional)

Setup Nginx reverse proxy (do not forget to override the max body size)

```
client_max_body_size 10G;
```

## CLI Setup

Since the access to the app through the website can be complicated, a CLI client is available (WIP) to access, download and upload content to Nyapix API.

### Requirements

- Python 13+
- PDM

### Setup

#### Config

```bash
cd LocalApp
cp config.json.example config.json
```

Don't forget to setup the configuration file `config.json`, replacing the API base URL with your own.

You can leave the token empty as it will be generated when you login to the API.

```bash
pdm install
```

PDM is used for now as a package is not ready yet, but it will be available soon when the API and CLI features matches.

### Run

```bash
pdm run main.py
```

The CLI should run fine if your configuration is correct, and you can now use it to login, upload and download content from the API.
