import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from books import BookCollection

import book_app


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(book_app, "BookCollection", BookCollection)
    # Monkeypatch the books module DATA_FILE via books module used by BookCollection
    import books

    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


def test_cli_add_and_list(capsys):
    # Add a book via CLI
    exit_code = book_app.run(["add", "--title", "Neuromancer", "--author", "William Gibson", "--year", "1984"]) 
    assert exit_code == 0

    # Now list and capture output
    exit_code = book_app.run(["list"]) 
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Neuromancer" in captured.out


def test_cli_remove():
    # Prepare collection
    coll = BookCollection()
    coll.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

    # Remove using CLI against the same data file
    exit_code = book_app.run(["remove", "--title", "The Hobbit"]) 
    assert exit_code == 0

    # Verify gone
    coll2 = BookCollection()
    assert coll2.find_book_by_title("The Hobbit") is None


def test_cli_find(capsys):
    coll = BookCollection()
    coll.add_book("Dune", "Frank Herbert", 1965)
    coll.add_book("Dune Messiah", "Frank Herbert", 1969)

    exit_code = book_app.run(["find", "--author", "Frank Herbert"]) 
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Dune" in captured.out
    assert "Dune Messiah" in captured.out
