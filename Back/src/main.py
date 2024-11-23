import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import fastapi

import endpoints.login as login_endpoints
import endpoints.users as users_endpoints

app = fastapi.FastAPI(debug=True)
bg_task = None

app.include_router(login_endpoints.router, prefix="")
app.include_router(users_endpoints.router, prefix="/users")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
