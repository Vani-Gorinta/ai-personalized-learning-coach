
from ai_service import generate_ai_response

try:
    print("Testing Gemini API connection...")

    response = generate_ai_response(
        "Explain Python programming in three simple sentences."
    )

    print("\nGemini Response:")
    print(response)

    print("\nGemini API connected successfully!")

except Exception as error:
    print("\nConnection failed:")
    print(error)
