from utility.logging import logger
import utility.users as users_utility
import bcrypt
import random

def setup_admin_user(db):
    """Register a new user in the database, returns True if the user was registered successfully, False otherwise"""
    cursor = db.cursor()

    setup_done = False

    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_+=!@#$%^&*()[]{}|;:,.<>?/"
    password = "".join(charset[random.randint(0, len(charset) - 1)] for _ in range(25))
    username = "admin"
    nickname = "admin"

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        # Count users in db
        cursor.execute("SELECT COUNT(*) FROM nyapixuser WHERE user_type = %s", (users_utility.USER_TYPE.ADMIN,))
        result = cursor.fetchone()
        if result[0] > 0:
            return

        cursor.execute(
            "INSERT INTO nyapixuser (username, nickname, password, user_type) VALUES (%s, %s, %s, %s)",
            (username, nickname, password_hash, users_utility.USER_TYPE.ADMIN)
        )
        db.commit()
        setup_done = True
    except Exception as e:
        logger.error("Error registering user")
        logger.error(e)
        return
    finally:
        cursor.close()
        if setup_done:
            logger.info("Setup done, here is the admin password: \"" + password + "\"")
