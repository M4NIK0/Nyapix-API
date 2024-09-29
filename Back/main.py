from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from os import getenv
import jwt
import uvicorn
import src.endpoints.login as login
import src.models.users as users_models

import src.endpoints.users.users as users_endpoints
import src.endpoints.tags.management as tags_endpoints

# Setup FastAPI app
app = FastAPI(openapi_url="/api/openapi.json", docs_url="/api/docs", name="AREA API - Ragnamod VI", version="Beta 0.0.1", title="Ragnamod VI")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

app.include_router(login.router, prefix="/api", tags=["Login"])
app.include_router(users_endpoints.router, prefix="/api/users", tags=["Users"])
app.include_router(tags_endpoints.router, prefix="/api/tags", tags=["Tags"])

@app.middleware("http")
async def check_auth(request: Request, call_next):
    if request.url.path.startswith("/api"):
        if request.url.path.startswith("/api/register") or request.url.path.startswith("/api/login") or request.url.path.startswith("/api/token") or request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/openapi.json"):
            response = await call_next(request)
            return response

        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return JSONResponse(content={"detail": "Not logged in"}, status_code=401)

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        except jwt.ExpiredSignatureError:
            return JSONResponse(content={"detail": "Token has expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse(content={"detail": "Invalid token"}, status_code=401)

    response = await call_next(request)
    return response

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)) -> users_models.User:
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        return users_models.User(id=payload.get("id"), username=payload.get("username"), type=payload.get("type"), creation_date=payload.get("creation_date"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
