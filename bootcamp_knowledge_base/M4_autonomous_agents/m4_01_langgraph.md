# LAB M4.01 - LangGraph: Strict Complaint Processor (Bloyce's Protocol)

## Use Case
Build a structured, rule-based complaint processing system using LangGraph. Every complaint about "Downside Up" phenomena must follow an exact sequence of steps with no deviation. This contrasts with the freeform LangChain agent from Lab 3.01.

## LangGraph vs LangChain Agent
- LangChain agent: LLM decides what to do next (flexible, unpredictable)
- LangGraph: YOU define exactly what happens in what order (predictable, auditable)

Think of it as the difference between a detective (LangChain - improvises) and a hospital admissions process (LangGraph - fixed protocol every time).

## Core Concepts

### State
State is a dictionary that travels through the entire graph. Every node reads from it and writes to it.
```python
from typing import TypedDict, Optional

class ComplaintState(TypedDict):
    complaint_id: str
    complaint_text: str
    complaint_type: Optional[str]
    is_valid: Optional[bool]
    investigation_notes: Optional[str]
    resolution: Optional[str]
    status: str
```
Think of state as a travelling folder: each desk (node) reads the folder, adds notes, and passes it to the next desk.

### Nodes
Nodes are just Python functions. Each one takes state in and returns updated state.
```python
def intake_node(state: ComplaintState) -> ComplaintState:
    # read the complaint text, assign an ID, set status to "received"
    return {**state, "status": "received"}
```

### Edges
Edges connect nodes. They can be fixed (always go to the same next node) or conditional (go to different nodes based on state).
```python
from langgraph.graph import StateGraph

graph = StateGraph(ComplaintState)
graph.add_node("intake", intake_node)
graph.add_node("validate", validate_node)
graph.add_edge("intake", "validate")           # fixed edge
graph.add_conditional_edges(                   # conditional edge
    "validate",
    decide_next_step,                          # function that returns node name
    {"valid": "investigate", "invalid": "reject"}
)
```

## Bloyce's Protocol: The 6 Nodes
1. `intake_node` - receives complaint, assigns ID, timestamps it
2. `validate_node` - checks complaint meets minimum requirements
3. `investigate_node` - classifies complaint type (portal, monster, psychic, environmental, other)
4. `resolve_node` - generates resolution based on complaint type
5. `close_node` - marks complaint as closed, generates summary
6. `rejection_node` - handles invalid complaints (bypasses main flow)

## Conditional Routing
```python
def decide_after_validate(state: ComplaintState) -> str:
    if state["is_valid"]:
        return "investigate"
    else:
        return "reject"
```
This function returns a string that matches one of the keys in `add_conditional_edges`.

## Key Learning
LangGraph is deterministic. The same complaint always follows the same path. This makes it auditable and predictable, which is critical for business processes that need consistency. The tradeoff is less flexibility - you have to anticipate every possible path upfront.

JSON Schema Validation: Pydantic can be used as a validation node to check that state fields have the correct types and values before passing to the next node.
```python
from pydantic import BaseModel, ValidationError

class ComplaintInput(BaseModel):
    complaint_text: str
    complaint_id: str

def validate_node(state):
    try:
        ComplaintInput(**state)
        return {**state, "is_valid": True}
    except ValidationError as e:
        return {**state, "is_valid": False, "error": str(e)}
```
