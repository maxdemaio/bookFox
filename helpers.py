import requests
import json

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
            return render_template("apology.html")
        return f(*args, **kwargs)
    return decorated_function


# (Reset API Key)
# Obtain response JSON from GoodReads API
def obtain_response(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "dNQrswehPpauusC6kI5wA", "isbns": f"{isbn}"})
    data = res.json()
    ratingsCount = data["books"][0]["ratings_count"]
    averageRating = data["books"][0]["average_rating"]

    return [ratingsCount, averageRating]

def hashPass(password):
    pass


