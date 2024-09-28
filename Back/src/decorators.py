from functools import wraps
from fastapi import Depends, HTTPException
from src.login_management import get_current_user
from src.models import users as users_models
import src.db_management.users as users_db


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
        if current_user.type != "admin":
            raise HTTPException(status_code=403, detail="Only admins can access this endpoint")
        return func(*args, **kwargs)
    return wrapper

def same_user_or_admin_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id: int = kwargs.get('user_id')
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if current_user.type != "admin" and current_user.id != user_id:
                raise HTTPException(status_code=403, detail="You can only access or edit your own data")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def same_user_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id: int = kwargs.get('user_id')
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if current_user.id != user_id:
                raise HTTPException(status_code=403, detail="You can only access or edit your own data")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def user_id_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id: int = kwargs.get('user_id')
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if not users_db.get_user_by_id(user_id):
                raise HTTPException(status_code=404, detail="User not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator
