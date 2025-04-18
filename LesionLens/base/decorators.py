from django.shortcuts import redirect
from functools import wraps

def approved_specialist_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.role == 'specialist' and user.is_approved:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper
