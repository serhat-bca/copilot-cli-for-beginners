const { describe, it, beforeEach } = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");
const { BookCollection, getBookStatistics } = require("../books");

let tempFile;

beforeEach(() => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "book-test-"));
  tempFile = path.join(tempDir, "data.json");
  fs.writeFileSync(tempFile, "[]");
});

describe("BookCollection", () => {
  it("should add a book", () => {
    const collection = new BookCollection(tempFile);
    const initialCount = collection.books.length;
    collection.addBook("1984", "George Orwell", 1949);
    assert.equal(collection.books.length, initialCount + 1);
    const book = collection.findBookByTitle("1984");
    assert.notEqual(book, null);
    assert.equal(book.author, "George Orwell");
    assert.equal(book.year, 1949);
    assert.equal(book.read, false);
  });

  it("should mark a book as read", () => {
    const collection = new BookCollection(tempFile);
    collection.addBook("Dune", "Frank Herbert", 1965);
    const result = collection.markAsRead("Dune");
    assert.equal(result, true);
    const book = collection.findBookByTitle("Dune");
    assert.equal(book.read, true);

    const reloadedCollection = new BookCollection(tempFile);
    assert.equal(reloadedCollection.findBookByTitle("Dune").read, true);
  });

  it("should return false when marking a nonexistent book as read", () => {
    const collection = new BookCollection(tempFile);
    const result = collection.markAsRead("Nonexistent Book");
    assert.equal(result, false);
  });

  it("should remove a book", () => {
    const collection = new BookCollection(tempFile);
    collection.addBook("The Hobbit", "J.R.R. Tolkien", 1937);
    const result = collection.removeBook("The Hobbit");
    assert.equal(result, true);
    const book = collection.findBookByTitle("The Hobbit");
    assert.equal(book, null);
  });

  it("should return false when removing a nonexistent book", () => {
    const collection = new BookCollection(tempFile);
    const result = collection.removeBook("Nonexistent Book");
    assert.equal(result, false);
  });
});

describe("getBookStatistics", () => {
  it("should return counts and oldest and newest books", () => {
    const books = [
      { title: "Dune", year: 1965, read: true },
      { title: "1984", year: 1949, read: false },
      { title: "The Hobbit", year: 1937, read: true },
    ];

    assert.deepEqual(getBookStatistics(books), {
      totalCount: 3,
      readCount: 2,
      unreadCount: 1,
      oldest: books[2],
      newest: books[0],
    });
  });

  describe("CLI", () => {
    it("should mark a book as read through the mark-as-read command", () => {
      const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "book-cli-test-"));
      fs.copyFileSync(path.join(__dirname, "..", "book_app.js"), path.join(appDir, "book_app.js"));
      fs.copyFileSync(path.join(__dirname, "..", "books.js"), path.join(appDir, "books.js"));
      fs.writeFileSync(
        path.join(appDir, "data.json"),
        JSON.stringify([{ title: "Dune", author: "Frank Herbert", year: 1965, read: false }])
      );

      const result = spawnSync(process.execPath, ["book_app.js", "mark-as-read"], {
        cwd: appDir,
        input: "Dune\n",
        encoding: "utf-8",
      });

      assert.equal(result.status, 0);
      assert.match(result.stdout, /Book marked as read/);
      assert.equal(JSON.parse(fs.readFileSync(path.join(appDir, "data.json"), "utf-8"))[0].read, true);
    });
  });

  it("should return zero counts and no oldest or newest book for an empty list", () => {
    assert.deepEqual(getBookStatistics([]), {
      totalCount: 0,
      readCount: 0,
      unreadCount: 0,
      oldest: null,
      newest: null,
    });
  });
});
