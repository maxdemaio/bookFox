from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            apology = "Please login, or register if you have not already made an account"
            return render_template("apology.html")
        return f(*args, **kwargs)
    return decorated_function