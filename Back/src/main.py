import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import fastapi

import endpoints.login as login_endpoints
import endpoints.users as users_endpoints

logger = logging.getLogger("main_logger")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler('logs/nyapix.log', maxBytes=1024*1024, backupCount=5)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

app = fastapi.FastAPI(debug=True)
bg_task = None

app.include_router(login_endpoints.router, prefix="")
app.include_router(users_endpoints.router, prefix="/users")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
