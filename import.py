# Insertion of book CSV data into the database
import csv

with open("books.csv") as csvFile:
    reader = csv.reader(csvFile)
    keys = next(reader)[:]
    books = list(reader)

print(keys)
print(books[0])
