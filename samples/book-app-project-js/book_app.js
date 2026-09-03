const readline = require("readline");
const { BookCollection, getBookStatistics } = require("./books");
const { printBooks } = require("./utils");

const collection = new BookCollection();

function handleList() {
  const books = collection.listBooks();
  printBooks(books);
}

function handleStatistics() {
  const statistics = getBookStatistics(collection.listBooks());
  const oldest = statistics.oldest
    ? `${statistics.oldest.title} (${statistics.oldest.year})`
    : "None";
  const newest = statistics.newest
    ? `${statistics.newest.title} (${statistics.newest.year})`
    : "None";

  console.log(`
Book Collection Statistics

Total books: ${statistics.totalCount}
Read: ${statistics.readCount}
Unread: ${statistics.unreadCount}
Oldest: ${oldest}
Newest: ${newest}
`);
}

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function handleAdd() {
  console.log("\nAdd a New Book\n");

  const title = await prompt("Title: ");
  const author = await prompt("Author: ");
  const yearStr = await prompt("Year: ");

  try {
    const year = yearStr ? parseInt(yearStr, 10) : 0;
    if (isNaN(year)) {
      throw new Error("Year must be a number.");
    }
    collection.addBook(title, author, year);
    console.log("\nBook added successfully.\n");
  } catch (err) {
    console.log(`\nError: ${err.message}\n`);
  }
}

function handleRemove() {
  return prompt("Enter the title of the book to remove: ").then((title) => {
    console.log("\nRemove a Book\n");
    collection.removeBook(title);
    console.log("\nBook removed if it existed.\n");
  });
}

async function handleMarkAsRead() {
  console.log("\nMark a Book as Read\n");

  const title = await prompt("Enter the title of the book to mark as read: ");
  const marked = collection.markAsRead(title);

  if (marked) {
    console.log("\nBook marked as read.\n");
  } else {
    console.log("\nBook not found.\n");
  }
}

async function handleFind() {
  console.log("\nFind Books by Author\n");

  const author = await prompt("Author name: ");
  const books = collection.findByAuthor(author);

  printBooks(books);
}

function showHelp() {
  console.log(`
Book Collection Helper

Commands:
  list     - Show all books
  statistics - Show collection statistics
  add      - Add a new book
  mark-as-read - Mark a book as read
  remove   - Remove a book by title
  find     - Find books by author
  help     - Show this help message
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    showHelp();
    return;
  }

  const command = args[0].toLowerCase();

  switch (command) {
    case "list":
      handleList();
      break;
    case "statistics":
      handleStatistics();
      break;
    case "add":
      await handleAdd();
      break;
    case "mark-as-read":
      await handleMarkAsRead();
      break;
    case "remove":
      await handleRemove();
      break;
    case "find":
      await handleFind();
      break;
    case "help":
      showHelp();
      break;
    default:
      console.log("Unknown command.\n");
      showHelp();
      break;
  }
}

main();
