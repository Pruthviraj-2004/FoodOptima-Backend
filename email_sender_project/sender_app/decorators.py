# sender_app/decorators.py

from django.shortcuts import redirect

def manager_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'manager_id' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')  # Replace 'login' with the name of your login URL
    return wrapper