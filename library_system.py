"""
Library Management System
---------------------------
An intermediate-level Python project demonstrating core
Object-Oriented Programming concepts:

- Encapsulation : private attributes with getters/setters
- Inheritance   : Book -> EBook / PrintedBook
- Polymorphism  : overridden describe() and borrow() methods
- Abstraction   : a simple Library class hiding internal logic

Run this file directly to see a demo of the system in action.
"""

from datetime import datetime, timedelta


# ----------------------------------------------------------------------
# Base class: Book
# ----------------------------------------------------------------------
class Book:
    """Base class representing a generic book in the library."""

    def __init__(self, title, author, isbn, copies=1):
        self.title = title
        self.author = author
        self.isbn = isbn
        self._copies_total = copies
        self._copies_available = copies

    # --- Encapsulation: controlled access to availability ---
    @property
    def copies_available(self):
        return self._copies_available

    def is_available(self):
        return self._copies_available > 0

    def borrow_copy(self):
        if self.is_available():
            self._copies_available -= 1
            return True
        return False

    def return_copy(self):
        if self._copies_available < self._copies_total:
            self._copies_available += 1
            return True
        return False

    # --- Polymorphism: subclasses override this ---
    def describe(self):
        return (f"'{self.title}' by {self.author} "
                f"({self._copies_available}/{self._copies_total} available)")

    def __str__(self):
        return self.describe()

    def __repr__(self):
        return f"Book(title={self.title!r}, isbn={self.isbn!r})"


# ----------------------------------------------------------------------
# Subclass: PrintedBook (inherits from Book)
# ----------------------------------------------------------------------
class PrintedBook(Book):
    """A physical, printed copy of a book. Has a shelf location."""

    LOAN_PERIOD_DAYS = 14

    def __init__(self, title, author, isbn, copies=1, shelf_location="A1"):
        super().__init__(title, author, isbn, copies)
        self.shelf_location = shelf_location

    def describe(self):
        base = super().describe()
        return f"[Printed] {base} - Shelf {self.shelf_location}"

    def due_date(self, borrow_date=None):
        borrow_date = borrow_date or datetime.now()
        return borrow_date + timedelta(days=self.LOAN_PERIOD_DAYS)


# ----------------------------------------------------------------------
# Subclass: EBook (inherits from Book)
# ----------------------------------------------------------------------
class EBook(Book):
    """A digital book. Unlimited 'copies' since it's just a file license,
    but we still track simultaneous active loans for realism."""

    LOAN_PERIOD_DAYS = 7

    def __init__(self, title, author, isbn, file_size_mb, max_concurrent_loans=3):
        super().__init__(title, author, isbn, copies=max_concurrent_loans)
        self.file_size_mb = file_size_mb

    def describe(self):
        base = super().describe()
        return f"[E-Book] {base} - {self.file_size_mb} MB"

    def due_date(self, borrow_date=None):
        borrow_date = borrow_date or datetime.now()
        return borrow_date + timedelta(days=self.LOAN_PERIOD_DAYS)


# ----------------------------------------------------------------------
# Member class
# ----------------------------------------------------------------------
class Member:
    """Represents a library member who can borrow books."""

    MAX_BOOKS_ALLOWED = 5

    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id
        self.borrowed_books = []  # list of (Book, due_date) tuples

    def can_borrow(self):
        return len(self.borrowed_books) < self.MAX_BOOKS_ALLOWED

    def add_borrowed_book(self, book, due_date):
        self.borrowed_books.append((book, due_date))

    def return_book(self, isbn):
        for entry in self.borrowed_books:
            if entry[0].isbn == isbn:
                self.borrowed_books.remove(entry)
                return entry[0]
        return None

    def list_borrowed(self):
        if not self.borrowed_books:
            return f"{self.name} has no borrowed books."
        lines = [f"{self.name}'s borrowed books:"]
        for book, due in self.borrowed_books:
            lines.append(f"  - {book.title} (due {due.strftime('%Y-%m-%d')})")
        return "\n".join(lines)

    def __str__(self):
        return f"Member: {self.name} (ID: {self.member_id})"


# ----------------------------------------------------------------------
# Library class: ties everything together
# ----------------------------------------------------------------------
class Library:
    """Manages the catalog of books and registered members."""

    def __init__(self, name):
        self.name = name
        self.catalog = {}   # isbn -> Book
        self.members = {}   # member_id -> Member

    def add_book(self, book):
        self.catalog[book.isbn] = book
        print(f"Added to catalog: {book.describe()}")

    def register_member(self, member):
        self.members[member.member_id] = member
        print(f"Registered new member: {member}")

    def borrow_book(self, member_id, isbn):
        member = self.members.get(member_id)
        book = self.catalog.get(isbn)

        if not member:
            print("Error: Member not found.")
            return False
        if not book:
            print("Error: Book not found in catalog.")
            return False
        if not member.can_borrow():
            print(f"Error: {member.name} has reached the borrowing limit.")
            return False
        if not book.borrow_copy():
            print(f"Error: '{book.title}' is currently unavailable.")
            return False

        due = book.due_date()
        member.add_borrowed_book(book, due)
        print(f"{member.name} borrowed '{book.title}', due {due.strftime('%Y-%m-%d')}.")
        return True

    def return_book(self, member_id, isbn):
        member = self.members.get(member_id)
        if not member:
            print("Error: Member not found.")
            return False

        book = member.return_book(isbn)
        if not book:
            print("Error: This member did not borrow that book.")
            return False

        book.return_copy()
        print(f"{member.name} returned '{book.title}'.")
        return True

    def show_catalog(self):
        print(f"\n--- {self.name} Catalog ---")
        for book in self.catalog.values():
            print(" ", book.describe())

    def show_members(self):
        print(f"\n--- {self.name} Members ---")
        for member in self.members.values():
            print(" ", member)


# ----------------------------------------------------------------------
# Demo / main program
# ----------------------------------------------------------------------
def main():
    library = Library("City Central Library")

    # Create books (demonstrates polymorphism: two different subclasses)
    book1 = PrintedBook("Clean Code", "Robert C. Martin", "978-0132350884",
                         copies=2, shelf_location="B3")
    book2 = EBook("Deep Learning", "Ian Goodfellow", "978-0262035613",
                   file_size_mb=45, max_concurrent_loans=2)
    book3 = PrintedBook("The Pragmatic Programmer", "Andrew Hunt", "978-0135957059",
                         copies=1, shelf_location="C1")

    for book in (book1, book2, book3):
        library.add_book(book)

    # Register members
    alice = Member("Alice Johnson", "M001")
    bob = Member("Bob Smith", "M002")
    library.register_member(alice)
    library.register_member(bob)

    library.show_catalog()
    library.show_members()

    print("\n--- Borrowing Activity ---")
    library.borrow_book("M001", "978-0132350884")  # Alice borrows Clean Code
    library.borrow_book("M002", "978-0262035613")  # Bob borrows Deep Learning
    library.borrow_book("M002", "978-0135957059")  # Bob borrows Pragmatic Programmer

    # Try borrowing a book with no copies left
    library.borrow_book("M001", "978-0135957059")  # should fail, Bob has the only copy

    print("\n--- Member Status ---")
    print(alice.list_borrowed())
    print(bob.list_borrowed())

    print("\n--- Returning Activity ---")
    library.return_book("M002", "978-0135957059")  # Bob returns Pragmatic Programmer
    library.borrow_book("M001", "978-0135957059")  # now Alice can borrow it

    library.show_catalog()


if __name__ == "__main__":
    main()
