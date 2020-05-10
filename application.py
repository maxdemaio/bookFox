import os

from flask import Flask, session, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from helpers import login_required, obtain_response

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    # Check to see if this makes them have to log back in
    # After visiting home page
    # # Forget user_id
    # session.clear()

    # User reached route via POST (as by submitting login via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("user"):
            msg = "Please provide a username. Return back home in order to log in again."
            return render_template("apology.html", msg=msg)

        # Ensure password was submitted
        elif not request.form.get("pass"):
            msg = "Please provide a password. Return back home in order to log in again."
            return render_template("apology.html", msg=msg)

        # TODO
        # # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                   username=request.form.get("username"))

        # # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid username and/or password", 403)

        # # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        # Redirect user to search page
        return redirect(url_for("search"))

    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Error handling (if user already taken)
        # INSERT username and pass(hashed) into db
        # show success message that they registered
        # return render_template("success.html")
        return render_template("register.html")

    else:
        return render_template("register.html")

@app.route("/search")
# @login_required
def search():
    return render_template("search.html")

@app.route("/results", methods=["POST"])
def results():
    # Obtain user's search query from form
    search = request.form['search']
    option = request.form['options']
    apology = False
    
    # Query db per user specification
    results = db.execute(f"""SELECT * FROM books 
        WHERE LOWER(books.{option}) LIKE LOWER(:search) ORDER BY year DESC;""", {"search": "%"+search+"%"}).fetchall()

    # No matches
    if len(results) == 0:
        apology = True

    return render_template("results.html", search=search, option=option, results=results, apology=apology)

@app.route("/reviews/<isbn>")
def reviews(isbn):

    # TODO
    # Contact the API using the isbn (retrieved by using id)
    # Render the books bage with all Goodreads info, and info from our website
    bookData = db.execute("""SELECT title, author, year FROM books WHERE isbn = :isbn""", {"isbn": isbn}).fetchone()

    if bookData == None:
        msg = "No book in our database matched that ISBN. Please return back to search to query again."
        return render_template("apology.html", msg=msg)

    title = bookData[0]
    author = bookData[1]
    year = bookData[2]

    # GoodReads API data
    apiData = obtain_response(isbn)
    ratingCount, averageRating = apiData[0], apiData[1]

    return render_template("reviews.html", title=title, author=author, 
        year=year, isbn=isbn, ratingCount=ratingCount, averageRating=averageRating)

@app.route("/api/<isbn>")
def api(isbn):
    # Contact my API using the isbn (retrieved by using id)
    return render_template("api.html", isbn=isbn)
