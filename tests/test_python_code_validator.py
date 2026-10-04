from services.assessment.python_code_validator import PythonCodeValidator


def test_command_line_quiz_structure():
    code = '''
questions = [
    {"question": "What keyword is used to define a function?", "answer": "def"},
    {"question": "What data type stores ordered items?", "answer": "list"},
    {"question": "Which keyword starts a loop?", "answer": "while"},
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

    print(f"Final score: {score}/{len(questions)}")


run_quiz()
'''

    result = PythonCodeValidator.validate(
        code,
        mission="Build a Command-Line Quiz",
    )

    assert result["syntax_valid"] is True
    assert result["criteria"]["quiz_questions"] is True
    assert result["criteria"]["answer_checking"] is True
    assert result["criteria"]["score_tracking"] is True
    assert result["criteria"]["multiple_questions"] is True
    assert result["criteria"]["final_score"] is True

def test_expense_tracker_requires_loop_for_multiple_expenses():
    code_without_loop = '''
expenses = []


def add_expense(expense):
    expenses.append(expense)


def calculate_total():
    return sum(expenses)


add_expense(50)
add_expense(25)
add_expense(30)

print("Expenses:", expenses)
print("Total:", calculate_total())
'''

    result_without_loop = PythonCodeValidator.validate(
        code_without_loop,
        mission="Build a Function-Based Expense Tracker",
    )

    assert result_without_loop["syntax_valid"] is True
    assert result_without_loop["criteria"]["expense_storage"] is True
    assert result_without_loop["criteria"]["add_expense_function"] is True
    assert result_without_loop["criteria"]["total_expense_function"] is True
    assert result_without_loop["criteria"]["multiple_expenses"] is False
    assert result_without_loop["criteria"]["expense_summary"] is True

    code_with_loop = '''
expenses = []


def add_expense(expense):
    expenses.append(expense)


def calculate_total():
    return sum(expenses)


for amount in [50, 25, 30]:
    add_expense(amount)

print("Expenses:", expenses)
print("Total:", calculate_total())
'''

    result_with_loop = PythonCodeValidator.validate(
        code_with_loop,
        mission="Build a Function-Based Expense Tracker",
    )

    assert result_with_loop["syntax_valid"] is True
    assert result_with_loop["criteria"]["expense_storage"] is True
    assert result_with_loop["criteria"]["add_expense_function"] is True
    assert result_with_loop["criteria"]["total_expense_function"] is True
    assert result_with_loop["criteria"]["multiple_expenses"] is True
    assert result_with_loop["criteria"]["expense_summary"] is True
