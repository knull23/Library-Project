from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library-books.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, to suppress warnings


# Create the base class
class Base(DeclarativeBase):
    pass


# Initialize the database extension
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Define the Book table/model
class Book(db.Model):
    __tablename__ = 'books'  # Table name
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


# Create the table schema in the database (requires application context)
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # READ ALL RECORDS
    # Construct a query to select all books ordered by title
    all_books = db.session.scalars(db.select(Book).order_by(Book.title)).all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Retrieve form data and handle possible conversion errors
        try:
            new_rating = float(request.form["rating"])  # Ensure rating is a float
            new_book = Book(
                title=request.form["title"],
                author=request.form["author"],
                rating=new_rating
            )
            db.session.add(new_book)
            db.session.commit()  # Commit the new book to the database
        except ValueError:
            # Handle cases where conversion to float fails
            return "Invalid rating value. Please enter a valid number.", 400
        return redirect(url_for('home'))
    return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # Retrieve book ID from the form safely
        book_id = request.form.get("id")
        if not book_id:
            return "Book ID is missing in the form submission.", 400

        book_to_update = db.get_or_404(Book, book_id)

        # Retrieve new rating from the form safely
        new_rating = request.form.get("new_rating")
        if not new_rating:
            return "New rating is missing in the form submission.", 400

        try:
            new_rating = float(new_rating)  # Ensure rating is a float
            book_to_update.rating = new_rating
            db.session.commit()  # Commit the changes to the database
        except ValueError:
            # Handle cases where conversion to float fails
            return "Invalid rating value. Please enter a valid number.", 400

        return redirect(url_for("home"))

    # Retrieve book ID from query parameters
    book_id = request.args.get('id')
    if not book_id:
        return "Book ID is missing in the request.", 400

    book_selected = db.get_or_404(Book, book_id)
    return render_template("edit.html", book=book_selected)


@app.route("/delete", methods=["GET"])
def delete():
    # Retrieve book ID from query parameters
    book_id = request.args.get('id')
    if not book_id:
        return "Book ID is missing in the request.", 400

    book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()  # Commit the delete action to the database
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)




