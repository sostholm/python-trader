from functools import wraps
from starlette.requests import Request
from starlette.exceptions import HTTPException


def guard(required_access=''):
    def decorator(func):
        @wraps(func)
        async def check_permissions(*args, **kwargs):
            
            request = args[1].context['request']
            assert isinstance(request, Request)
            payload = request.user.payload

            if not required_access in payload['access']: 
                raise HTTPException(status_code=403)
            
            return  await func(*args, **kwargs)
            
        return check_permissions
    return decorator
