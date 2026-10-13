const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Each product is an object stored in this array.
const products = [];

function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

function findProduct(searchTerm) {
  const term = searchTerm.toLowerCase();

  return products.find(
    (product) =>
      product.id.toLowerCase() === term ||
      product.name.toLowerCase() === term
  );
}

async function addProduct() {
  const id = await ask("Enter product ID: ");

  if (!id) {
    console.log("Product ID cannot be empty.");
    return;
  }

  // Product IDs must be unique.
  if (products.some((product) => product.id.toLowerCase() === id.toLowerCase())) {
    console.log("A product with this ID already exists. Use a unique ID.");
    return;
  }

  const name = await ask("Enter product name: ");

  if (!name) {
    console.log("Product name cannot be empty.");
    return;
  }

  const stockInput = await ask("Enter initial stock quantity: ");
  const stock = Number(stockInput);

  if (stockInput === "" || !Number.isInteger(stock) || stock < 0) {
    console.log("Stock must be a non-negative whole number.");
    return;
  }

  products.push({ id, name, stock });
  console.log(`Product "${name}" added successfully.`);
}

async function searchProduct() {
  const term = await ask("Enter product ID or exact name: ");
  const product = findProduct(term);

  if (product) {
    console.log(
      `ID: ${product.id} | Name: ${product.name} | Stock: ${product.stock}`
    );
  } else {
    console.log("Product not found.");
  }
}

async function updateStock() {
  const id = await ask("Enter the product ID to update: ");
  const product = products.find(
    (item) => item.id.toLowerCase() === id.toLowerCase()
  );

  if (!product) {
    console.log("Product not found.");
    return;
  }

  const stockInput = await ask("Enter the new stock quantity: ");
  const stock = Number(stockInput);

  if (stockInput === "" || !Number.isInteger(stock) || stock < 0) {
    console.log("Stock must be a non-negative whole number.");
    return;
  }

  product.stock = stock;
  console.log(`Stock updated. ${product.name} now has ${product.stock} units.`);
}

async function removeProduct() {
  const id = await ask("Enter the product ID to remove: ");
  const index = products.findIndex(
    (product) => product.id.toLowerCase() === id.toLowerCase()
  );

  if (index === -1) {
    console.log("Product not found.");
    return;
  }

  const removed = products.splice(index, 1);
  console.log(`Product "${removed[0].name}" removed successfully.`);
}

function displayInventory() {
  if (products.length === 0) {
    console.log("The inventory is empty.");
    return;
  }

  console.log("\n--- CURRENT INVENTORY ---");

  products.forEach((product, index) => {
    console.log(
      `${index + 1}. ID: ${product.id} | Name: ${product.name} | Stock: ${product.stock}`
    );
  });
}

async function main() {
  let running = true;

  while (running) {
    console.log("\n=== PRODUCT INVENTORY MANAGER ===");
    console.log("1. Add product");
    console.log("2. Search product");
    console.log("3. Update stock");
    console.log("4. Remove product");
    console.log("5. Display inventory");
    console.log("6. Exit");

    const choice = await ask("Choose an option (1-6): ");

    switch (choice) {
      case "1":
        await addProduct();
        break;
      case "2":
        await searchProduct();
        break;
      case "3":
        await updateStock();
        break;
      case "4":
        await removeProduct();
        break;
      case "5":
        displayInventory();
        break;
      case "6":
        running = false;
        console.log("Goodbye! Keep building your skills.");
        break;
      default:
        console.log("Invalid choice. Enter a number from 1 to 6.");
    }
  }

  rl.close();
}

main().catch((error) => {
  console.error("An unexpected error occurred:", error);
  rl.close();
});