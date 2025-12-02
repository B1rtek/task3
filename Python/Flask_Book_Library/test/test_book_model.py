import datetime

import pytest

from project import app, db
from project.books.models import Book


@pytest.fixture
def test_db():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

injections = [
    "';DROP TABLE books; --'",
    "<script>alert(\"xss\")</script>",
    "10; system('yes')",
    "| yes"
]

@pytest.mark.parametrize(
    ("name", "author", "year_published", "book_type", "status"),
    [
        ("Lalka", "Bolesław Prus", 1890, "2days", "available"),
        ("Solaris", "Stanisław Lem", 1961, "5days", "available"),
        ("Przedwiośnie", "Stefan Żeromski", 1924, "10days", "available")
    ]
)
def test_book_good(test_db, name, author, year_published, book_type, status):
    book = Book(name, author, year_published, book_type, status)
    test_db.session.add(book)
    test_db.session.commit()

    saved_book = Book.query.filter_by(name=name).first()
    assert saved_book.name == book.name
    assert saved_book.author == book.author
    assert saved_book.year_published == book.year_published
    assert saved_book.book_type == book.book_type
    assert saved_book.status == book.status


@pytest.mark.parametrize(
    "name",
    [
        "a" * 1000,
        "a" * 10000,
        "a" * 100000,
        "",
        "a\nb\nc"
    ]
)
def test_book_name_invalid(test_db, name):
    book = Book(name, "author", "1234", "2days")
    # unreasonably long (or empty) names should not be allowed, single line
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "name",
    [
        1000,
        10.0,
        None,
        {},
        []
    ]
)
def test_book_name_incorrect_type(test_db, name):
    book = Book(name, "author", "1234", "2days")
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "name", injections
)
def test_book_name_injections(test_db, name):
    book = Book(name, "author", "1234", "2days")
    # should not be saved in the db
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "author",
    [
        "a" * 1000,
        "a" * 10000,
        "a" * 100000,
        "",
        "a\nb\nc"
    ]
)
def test_book_author_invalid(test_db, author):
    book = Book("name", author, "1234", "2days")
    # unreasonably long (or empty) authors should not be allowed, single line
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "author",
    [
        1000,
        10.0,
        None,
        {},
        []
    ]
)
def test_book_author_incorrect_type(test_db, author):
    book = Book("name", author, "1234", "2days")
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "author", injections
)
def test_book_author_injections(test_db, author):
    book = Book("name", author, "1234", "2days")
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "year",
    [
        datetime.datetime.today().year + 1,
        2**32-1,
        -10**9
    ]
)
def test_book_year_invalid(test_db, year):
    book = Book("name", "author", year, "2days")
    # unreasonably long authors should not be allowed
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "year",
    [
        "a" * 10000,
        34.2,
        None,
        {},
        []
    ]
)
def test_book_year_incorrect_type(test_db, year):
    book = Book("name", "author", year, "2days")
    # should be int
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "year", injections
)
def test_book_year_injections(test_db, year):
    book = Book("name", "author", year, "2days")
    # should be int
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "book_type",
    [
        "",
        "3days",
        "a" * 10000
    ]
)
def test_book_book_type_invalid(test_db, book_type):
    book = Book("name", "author", 2002, book_type)
    # the only accepted values should be 2days, 5days, 10days per books/forms.py
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "book_type",
    [
        2002,
        34.2,
        None,
        {},
        []
    ]
)
def test_book_book_type_incorrect_type(test_db, book_type):
    book = Book("name", "author", 2002, book_type)
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "book_type", injections
)
def test_book_book_type_injections(test_db, book_type):
    book = Book("name", "author", 2002, book_type)
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "status",
    [
        "unavailable",
        "",
        "a" * 10000
    ]
)
def test_book_status_invalid(test_db, status):
    book = Book("name", "author", 2002, "2days", status)
    # the only valid status seems to be "available"?
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "status",
    [
        2002,
        34.2,
        None,
        {},
        []
    ]
)
def test_book_status_incorrect_type(test_db, status):
    book = Book("name", "author", 2002, "2days", status)
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


@pytest.mark.parametrize(
    "status", injections
)
def test_book_status_injections(test_db, status):
    book = Book("name", "author", 2002, "2days", status)
    # should be str
    with pytest.raises(Exception):
        test_db.session.add(book)
        test_db.session.commit()


