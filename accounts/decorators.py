from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            profile = getattr(request.user, "profile", None)
            if profile is None or profile.role not in roles:
                return HttpResponseForbidden("You do not have access to this page.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def shop_owner_required(view_func):
    return role_required(["shop_owner"])(view_func)


def college_user_required(view_func):
    return role_required(["college_user"])(view_func)
