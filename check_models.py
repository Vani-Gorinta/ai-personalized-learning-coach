from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Gemini API key not found.")
else:
    client = genai.Client(api_key=api_key)

    print("\nAvailable Gemini models:\n")

    try:
        for model in client.models.list():
            if "generateContent" in (model.supported_actions or []):
                print(model.name)

    except Exception as e:
        print("Error:", e)