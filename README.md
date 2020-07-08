# bookFox
### A book review web app with a Heroku/PostgreSQL base that utilizes Goodread's API. 

![](/static/bookFox.gif)

## Website description
Book Fox Once is a Flask web application where you can search for books, leave reviews for individual books, and see the reviews made by other people. The app also uses a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users are be able to query for book details and book reviews programmatically via the website’s API.

* In order to access the database of 5,000 books, read reviews by readers like you, and add your own reviews you must register and log in.

* After registering, you can query the database for book information based on ISBN, title, or author. In the results page clicking on the book's title displays the book review information. The book's ISBN is linked to an internal API which returns a JSON of the book id, isbn, average score, and number of reviews made.

* Once you've navigated to the book information page, you can view the GoodReads API information and reviews left by other Book Fox users. Finally, you may leave your own review of the current book by submitting the form.
