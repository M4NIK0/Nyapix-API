import models.users as users_models

def generate_session_token(user: users_models.UserModel) -> str:
    if user is None:
        raise ValueError("User cannot be None")
    return "token"
