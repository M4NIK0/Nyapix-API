import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import fastapi
from fastapi.security import APIKeyHeader
import time
import endpoints.login as login_endpoints
import endpoints.users as users_endpoints
import db_management.login as login_db
from db_management.connection import connect_db
from db_management.login import check_session
from db_management.setup import setup_admin_user
from utility.users import get_session

app = fastapi.FastAPI(debug=True)
bg_task = None

api_key_scheme = APIKeyHeader(name="Authorization", auto_error=False)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = fastapi.openapi.utils.get_openapi(
        title="Your API",
        version="1.0.0",
        description="API description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(login_endpoints.router, prefix="/v1")
app.include_router(users_endpoints.router, prefix="/v1/users")

db = None
while db is None:
    try:
        db = connect_db()
        setup_admin_user(db)
    except Exception as e:
        logging.error("Error connecting to database")
        logging.error(e)
        time.sleep(5)
    finally:
        if db is not None:
            db.close()

@app.middleware("http")
async def login_middleware(request: fastapi.Request, call_next):
    if request.url.path.startswith("/v1/login") or request.url.path.startswith("/v1/register") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        response = await call_next(request)
        return response
    db = None
    try:
        token = request.headers.get("Authorization").replace("Bearer ", "")
        if token is None:
            return fastapi.responses.Response(status_code=401, headers={"WWW-Authenticate": "Bearer realm=\"Login required\""})
        db = connect_db()
        if db is None or not check_session(db, token):
            return fastapi.responses.Response(status_code=401)
        user = login_db.get_session_user(db, token)
        session = get_session(token)
        if user is None or session is None or user.id != session.user_id:
            return fastapi.responses.Response(status_code=401)
        request.state.user = user
        request.state.session = session
        request.state.token = token
        response = await call_next(request)
        return response
    except Exception as e:
        logging.error("Error in login middleware")
        logging.error(e)
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")
    finally:
        if db is not None:
            db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
