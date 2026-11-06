
import os
import json
import re
import time
import random

from dotenv import load_dotenv
from google import genai


# =====================================================
# 1. LOAD GEMINI API CONFIGURATION
# =====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


MODEL_NAME = "gemini-2.5-flash"


# =====================================================
# 2. COMMON GEMINI RESPONSE FUNCTION
# =====================================================

def generate_ai_response(prompt):
    """
    Generate an AI response using Gemini.
    Includes retries for temporary server errors.
    """

    if not client:
        raise ValueError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in your .env file."
        )

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response.text

        except Exception as error:

            last_error = error

            error_message = str(error).upper()

            temporary_error = any(
                code in error_message
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "INTERNAL",
                    "502",
                    "504"
                ]
            )

            if temporary_error and attempt < 2:

                wait_time = (2 ** attempt) + random.uniform(0, 1)

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time:.1f} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise RuntimeError(
                    f"Gemini API error: {error}"
                ) from error

    raise RuntimeError(
        f"Gemini request failed: {last_error}"
    )


# =====================================================
# 3. PERSONALIZED STUDY PLAN GENERATION
# =====================================================

def generate_study_plan(
    subject,
    goal,
    level,
    duration,
    study_time
):
    """
    Generate a personalized day-by-day study plan.
    """

    prompt = f"""
    You are an expert AI Personalized Learning Coach.

    Create a detailed and practical study plan.

    STUDENT DETAILS:

    Subject: {subject}
    Learning Goal: {goal}
    Knowledge Level: {level}
    Duration: {duration} days
    Daily Study Time: {study_time} minutes

    REQUIREMENTS:

    1. Divide the plan day by day.
    2. Include specific topics.
    3. Provide clear learning objectives.
    4. Suggest practical exercises.
    5. Include revision sessions.
    6. Include assessments.
    7. Respect the available daily study time.
    8. Use simple and understandable language.
    9. Include a final assessment.
    10. Make the plan realistic for the student's level.

    FORMAT:

    Use clear headings, day-wise sections and bullet points.

    Include:
    - Daily topic
    - Learning objectives
    - Study activities
    - Practice exercises
    - Estimated time
    """

    return generate_ai_response(prompt)


# =====================================================
# 4. AI QUIZ GENERATION
# =====================================================

def generate_quiz(
    subject,
    topic,
    level,
    number_of_questions=5
):
    """
    Generate multiple-choice quiz questions using Gemini.
    Returns validated JSON data.
    """

    if not subject.strip():
        raise ValueError("Subject cannot be empty.")

    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    if not 1 <= number_of_questions <= 20:
        raise ValueError(
            "Number of questions must be between 1 and 20."
        )

    prompt = f"""
    You are an expert educational quiz generator.

    Generate exactly {number_of_questions} multiple-choice
    questions.

    SUBJECT: {subject}
    TOPIC: {topic}
    KNOWLEDGE LEVEL: {level}

    REQUIREMENTS:

    1. Generate exactly {number_of_questions} questions.
    2. Every question must have four options.
    3. Label options A, B, C and D.
    4. Only one option must be correct.
    5. Match the selected knowledge level.
    6. Include a short explanation for each answer.
    7. Avoid duplicate questions.
    8. Use accurate educational information.

    Return ONLY valid JSON.

    Required format:

    {{
        "subject": "{subject}",
        "topic": "{topic}",
        "questions": [
            {{
                "question": "Question text",
                "options": {{
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                }},
                "correct_answer": "A",
                "explanation": "Explanation of the answer"
            }}
        ]
    }}

    Do not include Markdown code fences or additional text.
    """

    response_text = generate_ai_response(prompt)

    # Extract JSON safely, including if Gemini adds code fences
    cleaned_response = response_text.strip()

    cleaned_response = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_response,
        flags=re.IGNORECASE
    )

    cleaned_response = re.sub(
        r"\s*```$",
        "",
        cleaned_response
    )

    try:

        quiz_data = json.loads(cleaned_response)

    except json.JSONDecodeError as error:

        raise ValueError(
            "Gemini returned invalid quiz JSON. Please try again."
        ) from error

    if not isinstance(quiz_data, dict):
        raise ValueError("Invalid quiz response format.")

    questions = quiz_data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("Quiz questions are missing.")

    if len(questions) != number_of_questions:
        raise ValueError(
            "The generated quiz has an incorrect number of questions."
        )

    required_options = {"A", "B", "C", "D"}

    for index, question in enumerate(questions):

        if not isinstance(question, dict):
            raise ValueError(
                f"Invalid question at position {index + 1}."
            )

        options = question.get("options")

        if not isinstance(options, dict):
            raise ValueError(
                f"Options missing in question {index + 1}."
            )

        if set(options.keys()) != required_options:
            raise ValueError(
                f"Question {index + 1} must contain A, B, C and D."
            )

        if any(
            not isinstance(options[key], str)
            or not options[key].strip()
            for key in required_options
        ):
            raise ValueError(
                f"Empty option found in question {index + 1}."
            )

        if question.get("correct_answer") not in required_options:
            raise ValueError(
                f"Invalid correct answer in question {index + 1}."
            )

        if not isinstance(question.get("question"), str):
            raise ValueError(
                f"Question text missing at position {index + 1}."
            )

        if not isinstance(question.get("explanation"), str):
            raise ValueError(
                f"Explanation missing in question {index + 1}."
            )

    quiz_data["subject"] = subject
    quiz_data["topic"] = topic

    return quiz_data


# =====================================================
# 5. AI TUTOR
# =====================================================

def generate_tutor_response(
    question,
    subject="General",
    level="Beginner",
    conversation_history=None
):
    """
    Generate educational explanations using Gemini AI.
    Supports follow-up questions.
    """

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    history = conversation_history or []

    conversation = ""

    for message in history[-10:]:

        role = message.get("role", "user")
        content = message.get("content", "")

        if role not in ["user", "assistant"]:
            continue

        conversation += (
            f"{role}: {content}\n"
        )

    prompt = f"""
    You are an intelligent and friendly AI Personalized Learning Coach.

    Help students understand concepts clearly.

    STUDENT DETAILS:

    Subject: {subject}
    Knowledge Level: {level}

    PREVIOUS CONVERSATION:

    {conversation}

    CURRENT STUDENT QUESTION:

    {question}

    INSTRUCTIONS:

    1. Explain concepts according to the student's level.
    2. Use simple and understandable language.
    3. Give practical examples.
    4. Break complicated concepts into smaller steps.
    5. Use headings and bullet points.
    6. Include code examples for programming questions.
    7. Answer follow-up questions using previous context.
    8. Encourage conceptual understanding.
    9. Politely redirect unrelated questions towards learning.

    Provide an accurate, clear and helpful educational answer.
    """

    return generate_ai_response(prompt)


# =====================================================
# 6. GENERAL AI EXPLANATION
# =====================================================

def generate_explanation(topic, subject="General"):
    """
    Generate a simple educational explanation for a topic.
    """

    prompt = f"""
    Explain the following topic as an experienced teacher.

    Subject: {subject}
    Topic: {topic}

    Include:

    1. Definition
    2. Important concepts
    3. Simple examples
    4. Practical applications
    5. Short summary

    Use simple language suitable for students.
    """

    return generate_ai_response(prompt)


# =====================================================
# END OF AI SERVICE
# =====================================================
