from functools import wraps
from fastapi import Depends, HTTPException
from src.login_management import get_current_user
from src.models import users as users_models
import src.db_management.users.users as users_db
import src.db_management.content.tags as tags_db
import src.db_management.content.authors as authors_db


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

def user_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if not users_db.get_user_by_username(current_user.username):
                raise HTTPException(status_code=401, detail="Invalid token")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def user_not_guest_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if current_user.type == 3:
                raise HTTPException(status_code=403, detail="As a guest user, you can't access this endpoint")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tag_id_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tag_id: int = kwargs.get('tag_id')
            if not tags_db.get_tag_by_id(tag_id):
                raise HTTPException(status_code=404, detail="Tag not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tag_name_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tag_name: str = kwargs.get('tag_name')
            if not tags_db.get_tag_by_name(tag_name):
                raise HTTPException(status_code=404, detail="Tag not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def tag_owner_or_admin_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tag_id: int = kwargs.get('tag_id')
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            tag = tags_db.get_tag_info_by_id(tag_id)
            if current_user.type != "admin" and tag.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="You can only access or edit your own data")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def author_id_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            author_id: int = kwargs.get('author_id')
            if not authors_db.get_author_by_id(author_id):
                raise HTTPException(status_code=404, detail="Author not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def author_name_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            author_name: str = kwargs.get('author_name')
            if not authors_db.get_author_by_name(author_name):
                raise HTTPException(status_code=404, detail="Author not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def author_owner_or_admin_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            author_id: int = kwargs.get('author_id')
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            author = authors_db.get_author_info_by_id(author_id)
            if current_user.type != "admin" and author.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="You can only access or edit your own data")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def author_existence_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user: users_models.User = kwargs.get('current_user', Depends(get_current_user))
            if not authors_db.get_author_by_name(current_user.username):
                raise HTTPException(status_code=404, detail="Author not found")
            return func(*args, **kwargs)
        return wrapper
    return decorator
