from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == role:
                return func(*args, **kwargs)
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("main.index"))
        return wrapper
    return decorator
