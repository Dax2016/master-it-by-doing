const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const tasks = [];

function ask(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

function addTask(taskName) {
  if (!taskName) {
    console.log("Task cannot be empty.");
    return;
  }

  tasks.push(taskName);
  console.log(`Task added: ${taskName}`);
}

function viewTasks() {
  if (tasks.length === 0) {
    console.log("Your to-do list is empty.");
    return;
  }

  console.log("\nYour tasks:");

  for (let i = 0; i < tasks.length; i++) {
    console.log(`${i + 1}. ${tasks[i]}`);
  }
}

function removeTask(taskNumber) {
  if (!Number.isInteger(taskNumber) ||
      taskNumber < 1 ||
      taskNumber > tasks.length) {
    console.log("Invalid task number. Please try again.");
    return;
  }

  const removed = tasks.splice(taskNumber - 1, 1);
  console.log(`Task removed: ${removed[0]}`);
}

async function main() {
  let running = true;

  console.log("=== CONSOLE TO-DO LIST ===");

  while (running) {
    console.log("\n1. Add task");
    console.log("2. View tasks");
    console.log("3. Remove task");
    console.log("4. Exit");

    const choice = await ask("Choose an option (1-4): ");

    switch (choice) {
      case "1": {
        const taskName = await ask("Enter a task: ");
        addTask(taskName);
        break;
      }

      case "2":
        viewTasks();
        break;

      case "3": {
        if (tasks.length === 0) {
          console.log("There are no tasks to remove.");
          break;
        }

        viewTasks();
        const input = await ask("Enter the task number to remove: ");
        const taskNumber = Number(input);

        if (input === "" || !Number.isInteger(taskNumber)) {
          console.log("Please enter a valid whole number.");
        } else {
          removeTask(taskNumber);
        }
        break;
      }

      case "4":
        running = false;
        console.log("Goodbye! Keep making progress.");
        break;

      default:
        console.log("Invalid choice. Enter a number from 1 to 4.");
    }
  }

  rl.close();
}

main().catch((error) => {
  console.error("The program encountered an error:", error);
  rl.close();
});