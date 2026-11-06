
from ai_service import generate_quiz
from database import save_quiz_attempt, get_quiz_history


# =====================================================
# 1. CREATE QUIZ
# =====================================================

def create_quiz(
    subject,
    topic,
    level,
    number_of_questions=5
):
    """Generate a quiz using Gemini AI."""

    quiz = generate_quiz(
        subject=subject,
        topic=topic,
        level=level,
        number_of_questions=number_of_questions
    )

    return quiz


# =====================================================
# 2. EVALUATE QUIZ
# =====================================================

def evaluate_quiz(quiz, submitted_answers):
    """Evaluate answers using Python and the answer key."""

    questions = quiz.get("questions", [])

    if not questions:
        raise ValueError("No quiz questions available.")

    score = 0
    results = []

    for index, question in enumerate(questions):

        question_number = index + 1
        correct_answer = question["correct_answer"]

        student_answer = submitted_answers.get(
            question_number
        )

        is_correct = student_answer == correct_answer

        if is_correct:
            score += 1

        results.append({
            "question_number": question_number,
            "question": question["question"],
            "student_answer": student_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })

    total_questions = len(questions)

    percentage = round(
        (score / total_questions) * 100,
        2
    )

    return {
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "results": results
    }


# =====================================================
# 3. GENERATE QUIZ FEEDBACK
# =====================================================

def generate_feedback(result):
    """Generate feedback based on quiz performance."""

    percentage = result["percentage"]

    if percentage > 80:
        return (
            "Excellent work! You have mastered the basics. "
            "Try a more challenging topic."
        )

    elif percentage >= 60:
        return (
            "Good effort! Review your incorrect answers "
            "and practise a few more questions."
        )

    else:
        return (
            "You need more practice. Revise the basic "
            "concepts and attempt another quiz."
        )


# =====================================================
# 4. SAVE QUIZ RESULT
# =====================================================

def save_quiz_result(
    learner_id,
    topic,
    result
):
    """Save quiz attempt and score in SQLite."""

    if learner_id is None:
        raise ValueError(
            "Please create a learner profile first."
        )

    attempt_id = save_quiz_attempt(
        learner_id=learner_id,
        topic=topic,
        score=result["score"],
        total_questions=result["total_questions"]
    )

    return attempt_id


# =====================================================
# 5. GENERATE ADAPTIVE RECOMMENDATION
# =====================================================

def generate_adaptive_recommendation(result, topic):
    """
    Recommend the next learning activity based on
    the learner's quiz performance.
    """

    percentage = result["percentage"]

    if percentage < 60:

        return {
            "topic": topic,
            "score_percentage": percentage,
            "performance": "Needs Improvement",
            "needs_revision": True,
            "next_action": "Revise Topic",
            "recommendation": (
                f"You scored {percentage}% in {topic}. "
                f"Revise the fundamental concepts of {topic}, "
                "review incorrect answers, and attempt another quiz."
            )
        }

    elif percentage <= 80:

        return {
            "topic": topic,
            "score_percentage": percentage,
            "performance": "Good",
            "needs_revision": False,
            "next_action": "Practise More",
            "recommendation": (
                f"You scored {percentage}% in {topic}. "
                "Review your mistakes and practise more "
                "questions before moving forward."
            )
        }

    else:

        return {
            "topic": topic,
            "score_percentage": percentage,
            "performance": "Excellent",
            "needs_revision": False,
            "next_action": "Move Forward",
            "recommendation": (
                f"Excellent! You scored {percentage}% in {topic}. "
                "You can move to the next topic or try "
                "advanced-level questions."
            )
        }


# =====================================================
# 6. IDENTIFY WEAK TOPIC
# =====================================================

def identify_weak_topic(result, topic):
    """Identify weak topics and recommend revision."""

    recommendation = generate_adaptive_recommendation(
        result,
        topic
    )

    return recommendation


# =====================================================
# 7. GET LATEST ADAPTIVE RECOMMENDATION
# =====================================================

def get_latest_adaptive_recommendation(learner_id):
    """
    Generate a recommendation using the learner's
    latest saved quiz attempt.
    """

    if learner_id is None:
        return None

    history = get_quiz_history(learner_id)

    if not history:
        return None

    latest_attempt = history[0]

    total_questions = latest_attempt["total_questions"]

    if total_questions <= 0:
        return None

    percentage = round(
        latest_attempt["score"] * 100 / total_questions,
        2
    )

    result = {
        "score": latest_attempt["score"],
        "total_questions": total_questions,
        "percentage": percentage
    }

    return generate_adaptive_recommendation(
        result,
        latest_attempt["topic"]
    )
