function printMenu() {
  console.log("\n📚 Book Collection App");
  console.log("1. Add a book");
  console.log("2. List books");
  console.log("3. Mark book as read");
  console.log("4. Remove a book");
  console.log("5. Exit");
}

function printBooks(books) {
  if (!books || books.length === 0) {
    console.log("No books found.");
    return;
  }

  console.log("\nYour Book Collection:\n");

  books.forEach((book, index) => {
    const status = book.read ? "✓" : " ";
    console.log(`${index + 1}. [${status}] ${book.title} by ${book.author} (${book.year})`);
  });

  console.log();
}

module.exports = { printMenu, printBooks };
