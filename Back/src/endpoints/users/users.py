from fastapi import APIRouter, Depends, HTTPException
import src.endpoints.users.me as me_endpoints

router = APIRouter()

router.include_router(me_endpoints.router, prefix="/me")
