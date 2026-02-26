# LAB M3.01 - LangChain Creative Complaint Handler

## Use Case
Build an AI agent for a fictional complaint bureau (inspired by Stranger Things) that handles complaints about "Downside Up" phenomena. The agent uses custom tools to look up cases, check monster databases, and generate creative responses.

## What is a LangChain Agent?
A LangChain agent is an LLM that can decide to use tools. Instead of just generating text, it can:
1. Read your question
2. Decide which tool (function) to call
3. Call the tool
4. Read the result
5. Decide if it needs another tool or if it can answer now
6. Return a final answer

This is called a ReAct loop (Reason + Act).

## Key Components

### Custom Tools with @tool decorator
```python
from langchain.tools import tool

@tool
def lookup_case(case_id: str) -> str:
    """Look up a complaint case by ID and return its details."""
    # your logic here
    return case_details
```
The docstring is important: the LLM reads it to decide when to use this tool.

### Prompt with MessagesPlaceholder
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a complaint handler for the Downside Up bureau."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
```
`agent_scratchpad` is where the agent writes its reasoning steps during the ReAct loop.

### AgentExecutor
```python
from langchain.agents import AgentExecutor, create_openai_tools_agent

agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "I saw a portal in my backyard"})
```

## Freeform Agent vs Structured Workflow
- LangChain agent: the LLM decides which tools to call and in what order. Flexible but unpredictable.
- LangGraph workflow: you define exactly which steps happen in which order. More predictable but less flexible.

Pitfall of freeform agents: the agent may skip tools, call tools in unexpected order, or add content beyond what tools returned. This is the key thing to note when comparing to LangGraph (Lab 4.01).

## Tool Usage Tracking Bug (Common Mistake)
The ToolUsageTracker showed zero usage because it was initialized AFTER the complaints ran, not before. Lesson: any tracking or logging object must be initialized before the code it is measuring runs.

## Key Learning
Parallel tool calling: OpenAI agents can call multiple tools simultaneously when the calls are independent. This is more efficient than calling them sequentially. The agent decides this automatically based on whether the tool results depend on each other.
