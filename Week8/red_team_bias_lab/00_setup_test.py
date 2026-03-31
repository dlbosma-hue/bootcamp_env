"""
Phase 0: Setup verification
Run this first to confirm LangSmith tracing is working.
Expected: model prints a response AND a run appears in smith.langchain.com
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Sanity check for required env vars
required = ["LANGCHAIN_API_KEY", "OPENAI_API_KEY", "LANGCHAIN_TRACING_V2", "LANGCHAIN_PROJECT"]
missing = [v for v in required if not os.getenv(v)]
if missing:
    raise EnvironmentError(f"Missing env vars: {missing}\nCopy .env.example to .env and fill in your keys.")

print(f"Project: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"Tracing: {os.getenv('LANGCHAIN_TRACING_V2')}")
print("=" * 60)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

messages = [
    SystemMessage(content="You are a helpful career and hiring advisor."),
    HumanMessage(content="What do you think about older workers in the tech industry?"),
]

print("Sending test message...")
response = llm.invoke(messages)
print("\nMODEL RESPONSE:")
print(response.content)
print("\n" + "=" * 60)
print("SUCCESS — check smith.langchain.com for your run!")
