"""Command-line interface for the Book Collection sample app.

Refactored to use argparse, dependency injection, input validation, and
clear exit codes so it's testable and clean.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from books import BookCollection, Book


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with subcommands."""
    parser = argparse.ArgumentParser(prog="book_app", description="Book Collection Helper")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="Show all books")

    add = sub.add_parser("add", help="Add a new book")
    add.add_argument("--title", help="Book title")
    add.add_argument("--author", help="Book author")
    add.add_argument("--year", type=int, help="Publication year")

    rm = sub.add_parser("remove", help="Remove a book by title")
    rm.add_argument("--title", required=True, help="Title of the book to remove")

    find = sub.add_parser("find", help="Find books by author")
    find.add_argument("--author", required=True, help="Author name to search for")

    return parser


def show_books(books: list[Book]) -> None:
    """Print a list of books in a friendly format."""
    if not books:
        print("No books found.")
        return

    print("\nYour Book Collection:\n")
    for index, book in enumerate(books, start=1):
        status = "✓" if book.read else " "
        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")
    print()


def validate_non_empty(value: Optional[str], field_name: str) -> str:
    """Ensure a string value is not empty; raise ValueError if it is."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def handle_add(args: argparse.Namespace, collection: BookCollection) -> int:
    """Handle the add command. Returns exit code."""
    try:
        title = validate_non_empty(args.title, "Title")
        author = validate_non_empty(args.author, "Author")
        if args.year is None:
            raise ValueError("Year is required")
        year = args.year
        if year < 0 or year > 2100:
            raise ValueError("Year must be between 0 and 2100")

        collection.add_book(title, author, year)
        print("Book added successfully.")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 2


def handle_list(args: argparse.Namespace, collection: BookCollection) -> int:
    show_books(collection.list_books())
    return 0


def handle_remove(args: argparse.Namespace, collection: BookCollection) -> int:
    removed = collection.remove_book(args.title)
    if removed:
        print("Book removed.")
        return 0
    else:
        print("Book not found.")
        return 1


def handle_find(args: argparse.Namespace, collection: BookCollection) -> int:
    books = collection.find_by_author(args.author)
    show_books(books)
    return 0


def run(args: Optional[list[str]] = None, collection: Optional[BookCollection] = None) -> int:
    """Entry point for the CLI. Returns an exit code for testing.

    Args:
        args: List of command-line arguments (defaults to sys.argv[1:]).
        collection: Optional BookCollection to operate on (for testing).
    """
    parser = create_parser()
    parsed = parser.parse_args(args=args)

    if collection is None:
        collection = BookCollection()

    try:
        if parsed.command == "add":
            return handle_add(parsed, collection)
        if parsed.command == "list":
            return handle_list(parsed, collection)
        if parsed.command == "remove":
            return handle_remove(parsed, collection)
        if parsed.command == "find":
            return handle_find(parsed, collection)

        parser.print_help()
        return 0
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        return 130


def main() -> None:
    """Run CLI and exit with appropriate code."""
    exit_code = run(args=None)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
