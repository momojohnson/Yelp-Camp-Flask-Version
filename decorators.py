from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

def check_confirmed(func):
    """
    A decorator that checks to ensure that a user
    has confirmed their email before they can have access to the application
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirm_email is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
