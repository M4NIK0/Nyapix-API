import utility.users as users_utility

def register(db, username: str, nickname: str, password: str) -> bool:
    """Register a new user in the database, returns True if the user was registered successfully, False otherwise"""
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO nyapixuser (username, nickname, password, user_type) VALUES (%s, %s, %s, %s)",
        (username, nickname, password, users_utility.USER_TYPE.GUEST)
    )
    db.commit()
    cursor.close()
    return True
