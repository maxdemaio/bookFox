import os
import settings

from flask import Flask, jsonify, session, redirect, render_template, request, url_for
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
    """Homepage"""

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
        print(os.getenv("API_KEY"))
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a user for Book Fox"""

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
            return render_template("apology.html", msg="Password did not meet required length.")

         # Check if both passwords match
        elif password != confirmation:
            return render_template("apology.html", msg="Passwords did not match.")

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
    """Display search options"""

    return render_template("search.html")

@app.route("/results", methods=["POST"])
def results():
    """Display search results"""

    # Obtain user's search query from search form
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


@app.route("/reviews/<isbn>", methods=["GET", "POST"])
@login_required
def reviews(isbn):
    """Display reviews, allow posting of reviews"""

    if request.method == "POST":
        # Obtain form data
        review = request.form["review"]
        score = request.form["options"]
        user_id = session["user_id"]

        # Get book ID of current book
        book_id = db.execute("""SELECT id FROM books WHERE isbn = :isbn""", {
                              "isbn": isbn}).fetchone()[0]

        # Check if user has already submitted a review for book
        if len(db.execute("SELECT * FROM reviews WHERE user_id = (:user_id)", {"user_id": user_id}).fetchall()) > 0:
            return render_template("apology.html", msg="You have already submitted a review for this book.")

        # Insert user review into the reviews table in the database
        db.execute("INSERT INTO reviews (user_id, book_id, score, review) VALUES (:user_id, :book_id, :score, :review)",
                   {"user_id": user_id, "book_id": book_id, "score": score, "review": review})
        db.commit()

        print(f"Inserted {review} with a score of {score} as {user_id}'s review of book {book_id}")

        # successfully submitted review page
        return redirect("/")

    else:
        # Check for the book in our database via ISBN
        bookData = db.execute("""SELECT title, author, year FROM books WHERE isbn = :isbn""", {"isbn": isbn}).fetchone()

        if bookData == None:
            msg = "No book in our database matched that ISBN. Please return back to search to query again."
            return render_template("apology.html", msg=msg)

        title = bookData[0]
        author = bookData[1]
        year = bookData[2]

        # Render the books page with all Goodreads API info
        apiData = obtain_response(isbn)
        ratingCount, averageRating = apiData[0], apiData[1]

        # Get book-ID of current book
        book_id = db.execute("""SELECT id FROM books WHERE isbn = :isbn""", {
            "isbn": isbn}).fetchone()[0]
        
        # Get reviews for current book
        reviews = db.execute("SELECT score,review FROM reviews WHERE book_id = (:book_id)", {"book_id": book_id}).fetchall()

        # Get users who have left a review for current book
        users = db.execute("""SELECT username FROM users WHERE id =
            (SELECT user_id FROM reviews WHERE book_id = (:book_id))""", {"book_id": book_id}).fetchall()
            
        return render_template("reviews.html", title=title, author=author, 
            year=year, isbn=isbn, ratingCount=ratingCount, 
            users=users, averageRating=averageRating, reviews=reviews)

@app.route("/api/<isbn>")
@login_required
def api(isbn):
    """Return details about a single book"""

    # Check if book exists
    if db.execute("""SELECT id FROM books WHERE isbn = :isbn""", {"isbn": isbn}).fetchone() == None:
        return jsonify({"error": "Invalid ISBN"})

    # Get book_id
    book_id = db.execute("""SELECT id FROM books WHERE isbn = :isbn""", {
        "isbn": isbn}).fetchone()[0]

    # Get book (id, isbn, review_count, average_score)
    review_info = db.execute("""SELECT AVG(score),COUNT(*) FROM reviews 
        WHERE book_id = :book_id""", {"book_id": book_id}).fetchall()

    book_info = {
        "isbn": isbn,
        "book_id": book_id,
        "average_score": review_info[0][0],
        "review_count": review_info[0][1]
    }

    # Display API data
    return jsonify(book_info)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
