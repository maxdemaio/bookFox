import os

from flask import Flask, session, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

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
    # User reached route via POST (as by submitting login via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form["user"]:
            return render_template("apology.html", msg="Please provide a username. Return back home in order to log in again.")

        # Ensure password was submitted
        elif not request.form["pass"]:
            return render_template("apology.html", msg="Please provide a password. Return back home in order to log in again.")

        # All checks passed
        # Query database for username
        else:
            rows = db.execute("SELECT * FROM users WHERE username = (:username)",
                            {"username": request.form["user"]}).fetchall()

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0][2], request.form["pass"]):
                return render_template("apology.html", msg="Invalid username and/or password")

            # Remember which user has logged in
            session["user_id"] = rows[0][0]

            # Redirect user to search page
            return redirect(url_for("search"))

    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Grab data from form
        username = request.form['user']
        password = request.form['password']
        confirmation = request.form['confirmation']
        password_hash = generate_password_hash(password)

        # Check if username is already taken (check db)
        if len(db.execute("SELECT * FROM users WHERE username = (:username)", {"username": username}).fetchall()) > 0:
            return render_template("register.html", apology=True)

        # Check if username has valid length 
        elif len(username) < 3:
            return render_template("apology.html", msg="Username did not meet required length")

        # Check if password has valid length
        elif len(password) < 5:
            return render_template("apology.html", msg="Password did not meet required length")

         # Check if both passwords match
        elif password != confirmation:
            return render_template("apology.html", msg="Passwords did not match")

        # All checks met
        else:
            # Register the user
            db.execute("INSERT INTO users (username, passhash) VALUES (:username, :password_hash)",
                       {"username": username, "password_hash": password_hash})
            db.commit()
            return redirect("/")

    else:
        return render_template("register.html", apology=False)

@app.route("/search")
@login_required
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
        WHERE LOWER(books.{option}) LIKE LOWER(:search) ORDER BY year DESC;""", 
        {"search": "%"+search+"%"}).fetchall()

    # No matches
    if len(results) == 0:
        apology = True

    return render_template("results.html", search=search, option=option, results=results, apology=apology)

@app.route("/reviews/<isbn>")
@login_required
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
@login_required
def api(isbn):
    # Contact my API using the isbn (retrieved by using id)
    return render_template("api.html", isbn=isbn)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
