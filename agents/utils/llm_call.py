# utils/llm_call.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API key from environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use Gemini Pro 2.0
model = genai.GenerativeModel("gemini-2.0-flash")

def call_llm_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 20,
                "max_output_tokens": 1024,
                "stop_sequences": None
            }
        )
        return response.text
    except Exception as e:
        return f"[ERROR calling Gemini]: {str(e)}"
