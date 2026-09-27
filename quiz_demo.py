questions = [
    {
        "question": "What keyword is used to define a function in Python?",
        "answer": "def"
    },
    {
        "question": "What data type stores an ordered collection of items?",
        "answer": "list"
    },
    {
        "question": "Which keyword starts a loop that continues while a condition is true?",
        "answer": "while"
    }
]


def run_quiz():
    score = 0

    for item in questions:
        print(item["question"])
        answer = input("Your answer: ").strip().lower()

        if answer == item["answer"]:
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. The correct answer is {item['answer']}.")

    print(f"\nFinal score: {score}/{len(questions)}")


run_quiz()
