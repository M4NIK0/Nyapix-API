# Nyapix API

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

### Step 2

Start docker compose of the project

```bash
docker compose up --build
```

> Since it is your first startup, the backend will generate an admin account for you to use to finish the whole setup from the frontend.

### Step 3

Login to the admin account on the website, change its password and username (it will be more secure)

### Step 4 (optional)

Setup Nginx reverse proxy (do not forget to override the max body size)

```
client_max_body_size 10G;
```
