import fastapi
import functools
import utility.users as users_utility

def admin_required(func):
    @functools.wraps(func)
    async def wrapper(request: fastapi.Request, *args, **kwargs):
        if request.state.user.type != users_utility.USER_TYPE.ADMIN:
            return fastapi.responses.Response(status_code=403)
        return await func(request, *args, **kwargs)
    return wrapper
