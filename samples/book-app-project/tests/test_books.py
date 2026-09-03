import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import books
from books import BookCollection


@pytest.fixture(autouse=True)
def use_temp_data_file(tmp_path, monkeypatch):
    """Use a temporary data file for each test."""
    temp_file = tmp_path / "data.json"
    temp_file.write_text("[]")
    monkeypatch.setattr(books, "DATA_FILE", str(temp_file))


@pytest.fixture
def collection():
    """Provide an empty collection backed by the test data file."""
    return BookCollection()


class TestBookCollectionInitialization:
    """Tests for loading book data."""

    def test_starts_empty_when_data_file_contains_empty_list(self, collection):
        assert collection.list_books() == []

    def test_starts_empty_when_data_file_is_missing(self, tmp_path, monkeypatch):
        missing_file = tmp_path / "missing.json"
        monkeypatch.setattr(books, "DATA_FILE", str(missing_file))

        assert BookCollection().list_books() == []

    def test_starts_empty_when_data_file_is_corrupted(
        self, tmp_path, monkeypatch, capsys
    ):
        corrupted_file = tmp_path / "data.json"
        corrupted_file.write_text("{not valid json")
        monkeypatch.setattr(books, "DATA_FILE", str(corrupted_file))

        collection = BookCollection()

        assert collection.list_books() == []
        assert "corrupted" in capsys.readouterr().out

    def test_loads_saved_fields_including_read_status(
        self, tmp_path, monkeypatch
    ):
        data_file = tmp_path / "data.json"
        data_file.write_text(
            '[{"title": "Dune", "author": "Frank Herbert", '
            '"year": 1965, "read": true}]'
        )
        monkeypatch.setattr(books, "DATA_FILE", str(data_file))

        collection = BookCollection()

        assert collection.list_books() == [
            books.Book("Dune", "Frank Herbert", 1965, True)
        ]


class TestAddBook:
    """Tests for adding books."""

    def test_adds_book_with_expected_fields(self, collection):
        result = collection.add_book("1984", "George Orwell", 1949)

        assert result.title == "1984"
        assert result.author == "George Orwell"
        assert result.year == 1949
        assert result.read is False
        assert collection.list_books() == [result]

    def test_adds_multiple_books_in_insertion_order(self, collection):
        first = collection.add_book("1984", "George Orwell", 1949)
        second = collection.add_book("Dune", "Frank Herbert", 1965)

        assert collection.list_books() == [first, second]

    @pytest.mark.parametrize(
        ("title", "author"),
        [
            ("", "Author"),
            ("Title", ""),
            ("", ""),
        ],
    )
    def test_adds_books_with_empty_text_fields(
        self, collection, title, author
    ):
        result = collection.add_book(title, author, 0)

        assert result.title == title
        assert result.author == author
        assert len(collection.list_books()) == 1

    def test_added_book_is_persisted(self, collection):
        collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

        reloaded = BookCollection()

        assert reloaded.find_book_by_title("The Hobbit") is not None
        assert reloaded.find_book_by_title("The Hobbit").year == 1937

    def test_allows_duplicate_titles_as_separate_books(self, collection):
        first = collection.add_book("Dune", "Frank Herbert", 1965)
        second = collection.add_book("Dune", "Brian Herbert", 1999)

        assert collection.list_books() == [first, second]


class TestFindBookByTitle:
    """Tests for title searches."""

    @pytest.mark.parametrize("query", ["1984", "nInEtEeN84", " 1984 "])
    def test_finds_matching_title_case_insensitively(
        self, collection, query
    ):
        title = "NINETEEN84" if query == "nInEtEeN84" else "1984"
        collection.add_book(title, "George Orwell", 1949)

        result = collection.find_book_by_title(query)

        if query == " 1984 ":
            assert result is None
        else:
            assert result is not None
            assert result.title == title

    def test_returns_first_match_when_titles_are_duplicated(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.add_book("Dune", "Brian Herbert", 1999)

        result = collection.find_book_by_title("DUNE")

        assert result is not None
        assert result.author == "Frank Herbert"

    @pytest.mark.parametrize("query", ["", "Missing"])
    def test_returns_none_for_empty_collection_or_missing_title(
        self, collection, query
    ):
        assert collection.find_book_by_title(query) is None

    def test_returns_none_when_title_does_not_match(self, collection):
        collection.add_book("1984", "George Orwell", 1949)

        assert collection.find_book_by_title("Animal Farm") is None


class TestFindByAuthor:
    """Tests for author searches."""

    def test_finds_all_books_by_author_case_insensitively(self, collection):
        collection.add_book("1984", "George Orwell", 1949)
        collection.add_book("Animal Farm", "George Orwell", 1945)
        collection.add_book("Dune", "Frank Herbert", 1965)

        result = collection.find_by_author("gEoRgE oRwElL")

        assert [book.title for book in result] == ["1984", "Animal Farm"]

    @pytest.mark.parametrize("author", ["", "Unknown"])
    def test_returns_empty_list_for_empty_collection_or_missing_author(
        self, collection, author
    ):
        assert collection.find_by_author(author) == []

    def test_returns_empty_list_when_author_has_no_matches(self, collection):
        collection.add_book("1984", "George Orwell", 1949)

        assert collection.find_by_author("Frank Herbert") == []

    def test_matches_books_with_empty_author(self, collection):
        collection.add_book("Untitled", "", 2024)

        result = collection.find_by_author("")

        assert [book.title for book in result] == ["Untitled"]


class TestMarkAsRead:
    """Tests for changing a book's read status."""

    def test_marks_matching_book_as_read(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)

        result = collection.mark_as_read("dUnE")

        assert result is True
        assert collection.find_book_by_title("Dune").read is True

    def test_marking_a_book_twice_remains_successful_and_read(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)

        assert collection.mark_as_read("Dune") is True
        assert collection.mark_as_read("Dune") is True
        assert collection.find_book_by_title("Dune").read is True

    def test_marked_status_is_persisted(self, collection):
        collection.add_book("Dune", "Frank Herbert", 1965)
        collection.mark_as_read("Dune")

        reloaded = BookCollection()

        assert reloaded.find_book_by_title("Dune").read is True

    @pytest.mark.parametrize("title", ["Missing", ""])
    def test_returns_false_without_changing_empty_or_missing_collection(
        self, collection, title
    ):
        assert collection.mark_as_read(title) is False
        assert collection.list_books() == []


class TestRemoveBook:
    """Tests for removing books."""

    def test_removes_matching_book(self, collection):
        collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)

        result = collection.remove_book("the hobbit")

        assert result is True
        assert collection.find_book_by_title("The Hobbit") is None
        assert collection.list_books() == []

    def test_removes_only_the_matching_book(self, collection):
        collection.add_book("1984", "George Orwell", 1949)
        collection.add_book("Dune", "Frank Herbert", 1965)

        assert collection.remove_book("1984") is True
        assert [book.title for book in collection.list_books()] == ["Dune"]

    def test_removes_only_the_first_duplicate_title(self, collection):
        first = collection.add_book("Dune", "Frank Herbert", 1965)
        second = collection.add_book("Dune", "Brian Herbert", 1999)

        assert collection.remove_book("Dune") is True
        assert collection.list_books() == [second]
        assert first not in collection.list_books()

    def test_removal_is_persisted(self, collection):
        collection.add_book("The Hobbit", "J.R.R. Tolkien", 1937)
        collection.remove_book("The Hobbit")

        assert BookCollection().list_books() == []

    @pytest.mark.parametrize("title", ["Missing", ""])
    def test_returns_false_without_changing_empty_or_missing_collection(
        self, collection, title
    ):
        assert collection.remove_book(title) is False
        assert collection.list_books() == []
