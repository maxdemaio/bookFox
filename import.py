# Create table and insertion of book CSV data into the database
import csv
import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

print(db.execute("""SELECT * FROM books;""").fetchone())

# # Create  books, users, and reviews tables
# db.execute("""CREATE TABLE books (
#         id SERIAL PRIMARY KEY,
#         isbn TEXT NOT NULL UNIQUE,
#         title TEXT NOT NULL,
#         author TEXT NOT NULL,
#         year INTEGER NOT NULL
#         )""")

# db.execute(""" CREATE TABLE users (
#         id SERIAL PRIMARY KEY,
#         username TEXT NOT NULL UNIQUE,
#         passhash TEXT NOT NULL
#         )""")

# db.execute(""" CREATE TABLE reviews (
#         id SERIAL PRIMARY KEY,
#         user_id INTEGER REFERENCES users,
#         book_id INTEGER REFERENCES books,
#         score REAL NOT NULL,
#         review TEXT
#         )""")

# Commit changes
# db.commit()



# # Insert data into the en_tense table in our db
# with open('books.csv') as csvFile:
#     reader = csv.DictReader(csvFile)
    
#     for row in reader:
#         isbn = row['isbn']
#         title = row['title']
#         author = row['author']
#         year = row['year']
#         print("Inserted", isbn, title, author, year)

#         db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
#             {"isbn":isbn, "title": title, "author":author, "year":year})

# db.commit()
