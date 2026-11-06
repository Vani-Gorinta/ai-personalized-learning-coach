
from ai_service import (
    generate_study_plan,
    generate_quiz,
    generate_tutor_response
)

print("\n========== TEST 1: STUDY PLAN ==========")

try:

    plan = generate_study_plan(
        subject="Python",
        goal="Learn Python fundamentals",
        level="Beginner",
        duration=7,
        study_time=45
    )

    print(plan)

except Exception as error:
    print("Study plan error:", error)


print("\n========== TEST 2: QUIZ ==========")

try:

    quiz = generate_quiz(
        subject="Python",
        topic="Python Variables",
        level="Beginner",
        number_of_questions=5
    )

    for index, question in enumerate(
        quiz["questions"], start=1
    ):

        print(f"\nQuestion {index}:")
        print(question["question"])
        print(question["options"])

except Exception as error:
    print("Quiz error:", error)


print("\n========== TEST 3: AI TUTOR ==========")

try:

    answer = generate_tutor_response(
        question="Explain Python loops with an example.",
        subject="Python",
        level="Beginner"
    )

    print(answer)

except Exception as error:
    print("Tutor error:", error)
