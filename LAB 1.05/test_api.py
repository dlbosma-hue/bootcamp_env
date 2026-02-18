import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Test with a simple call
print("Testing API connection...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say 'API is working!' if you can read this."}
    ]
)

print(response.choices[0].message.content)
print("\n✓ API setup successful!")