import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Ensure the Groq API key is present
# Note: The Groq client automatically looks for the GROQ_API_KEY environment variable.
# Since we stored it as OPENAI_API_KEY in .env, we can pass it explicitly.
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "your-groq-api-key-here":
    print("Please set your Groq API key in the .env file (as OPENAI_API_KEY).")
    exit(1)

client = Groq(api_key=api_key)

print("Sending request to Groq (llama-3.1-8b-instant)...\n")

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "user",
        "content": "Hi! Can you tell me a fun fact about real estate?"
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")

print("\n\nDone!")
