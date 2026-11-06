
from quiz_manager import create_quiz, evaluate_quiz, generate_feedback

# Generate quiz
quiz = create_quiz(
    subject="Python Programming",
    topic="Python Variables",
    level="Beginner",
    number_of_questions=5
)

print("\nQUIZ GENERATED SUCCESSFULLY")

# Display questions
for index, question in enumerate(quiz["questions"], start=1):

    print(f"\nQuestion {index}: {question['question']}")

    for option, value in question["options"].items():
        print(f"{option}. {value}")

# Sample answers for testing
sample_answers = {
    1: "A",
    2: "B",
    3: "C",
    4: "A",
    5: "D"
}

# Evaluate answers
result = evaluate_quiz(
    quiz,
    sample_answers
)

print("\nQUIZ RESULTS")

print("Score:", result["score"])
print("Total:", result["total_questions"])
print("Percentage:", result["percentage"], "%")

print("\nFEEDBACK")

print(generate_feedback(result))

print("\nDETAILED RESULTS")

for item in result["results"]:

    print("\nQuestion:", item["question_number"])
    print("Your Answer:", item["student_answer"])
    print("Correct Answer:", item["correct_answer"])
    print("Correct:", item["is_correct"])
    print("Explanation:", item["explanation"])
