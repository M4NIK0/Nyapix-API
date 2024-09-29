from fastapi import Depends, HTTPException, APIRouter
from src.login_management import get_current_user
from src.logs import logger
import src.models.general_responses as general_responses_models
import src.models.users as users_models
import src.decorators as decorators


router = APIRouter()
