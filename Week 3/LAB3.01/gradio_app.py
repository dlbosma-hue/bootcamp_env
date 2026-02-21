import gradio as gr
import os
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

# ── Tools ─────────────────────────────────────────────────────────────────────────────

@tool
def consult_demogorgon(complaint: str) -> str:
    """Get the Demogorgon's perspective on a complaint about the Upside Down.

    Args:
        complaint: The complaint about the Upside Down
    Returns:
        The Demogorgon's perspective (creative and possibly chaotic)
    """
    responses = [
        f"The Demogorgon tilts its head. It seems confused by '{complaint}'. Perhaps the issue is that you're thinking in three dimensions?",
        f"The Demogorgon makes a sound that might be agreement. It suggests that the problem might be temporal - things work differently in the Upside Down's time.",
        f"The Demogorgon appears to be eating something. It doesn't seem to understand the concept of '{complaint}' - maybe consistency isn't a priority there?",
    ]
    return random.choice(responses)


@tool
def check_hawkins_records(query: str) -> str:
    """Search Hawkins historical records for information.

    Args:
        query: What to search for in the records
    Returns:
        Information from Hawkins historical records
    """
    records = {
        "portal": "Records show portals have opened on various dates with no clear pattern. Weather, electromagnetic activity, and unknown factors seem involved.",
        "monsters": "Historical records indicate creatures from the Upside Down behave differently based on environmental factors, time of day, and proximity to certain individuals.",
        "psychics": "Records show that psychic abilities vary greatly. Some individuals can move objects but not see the future, others can see visions but not move things.",
        "electricity": "Hawkins has a history of electrical anomalies. Records suggest a connection between the Upside Down and electromagnetic fields.",
    }
    for key, value in records.items():
        if key in query.lower():
            return value
    return f"Records don't contain specific information about '{query}', but many unexplained events have occurred in Hawkins over the years."


@tool
def cast_interdimensional_spell(problem: str, creativity_level: str = "medium") -> str:
    """Suggest a creative interdimensional spell to fix a problem.

    Args:
        problem: The problem to solve
        creativity_level: How creative to be (low, medium, high)
    Returns:
        A creative spell or solution suggestion
    """
    creativity_multiplier = {"low": 1, "medium": 2, "high": 3}[creativity_level]
    spells = [
        f"Try chanting 'Bemca Becma Becma' three times while holding a Walkman. This might recalibrate the interdimensional frequencies related to: {problem}",
        f"Create a salt circle and place a compass in the center. The magnetic anomalies might help stabilize: {problem}",
        f"Play 'Running Up That Hill' backwards at the exact location of the issue. The temporal resonance could fix: {problem}",
        f"Gather three items: a lighter, a compass, and something personal. Arrange them in a triangle while thinking about: {problem}. The emotional connection might help.",
    ]
    selected = random.sample(spells, min(creativity_multiplier, len(spells)))
    return "\n".join(selected)


@tool
def gather_party_wisdom(question: str) -> str:
    """Ask the D&D party (Mike, Dustin, Lucas, Will) for their collective wisdom.

    Args:
        question: The question or problem to ask the party about
    Returns:
        The party's collective wisdom and suggestions
    """
    party_responses = {
        "portal": "Mike: 'Portals are unpredictable, but they usually open near strong emotional events or electromagnetic disturbances.' Dustin: 'Also, they seem to follow some kind of pattern related to the Mind Flayer's activity.'",
        "monsters": "Lucas: 'Demogorgons are territorial but also opportunistic.' Will: 'They can sense fear and strong emotions. Maybe that's why they act differently sometimes.'",
        "psychics": "Mike: 'El's powers seem connected to her emotional state.' Dustin: 'And they're limited by her physical and mental energy. That's probably why she can't do everything.'",
        "electricity": "Lucas: 'The Upside Down seems to interfere with electrical systems.' Dustin: 'But it also creates strange connections. It's like a feedback loop.'",
    }
    for key, response in party_responses.items():
        if key in question.lower():
            return response
    return "The party huddles together. Mike: 'This is a tough one.' Dustin: 'We need more information.' Lucas: 'Let\'s think about what we know.' Will: 'Maybe we should consult other sources?'"


# ── Agent ─────────────────────────────────────────────────────────────────────────────

tools = [consult_demogorgon, check_hawkins_records, cast_interdimensional_spell, gather_party_wisdom]

SYSTEM_PROMPT = """You are Becma, the creative chaos agent of the Downside-Up Complaint Bureau.

Your job is to handle complaints about inconsistencies in the Normal Objects universe
(a Stranger Things inspired world) in a creative and entertaining way.

You have access to several tools to help you investigate and resolve complaints:
- consult_demogorgon: Get the Demogorgon's unique perspective
- check_hawkins_records: Search historical records for patterns
- cast_interdimensional_spell: Suggest creative magical solutions
- gather_party_wisdom: Ask Mike, Dustin, Lucas and Will for insights

You MUST use at least 2 tools to investigate every complaint before writing your response.
Always provide an entertaining, creative resolution to each complaint.

Remember: In the Normal Objects universe, inconsistency IS the rule, not the exception!"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


# ── Handler ─────────────────────────────────────────────────────────────────────────────

def handle_complaint(complaint: str):
    if not complaint.strip():
        return "Please enter a complaint.", ""

    result = agent.invoke({"messages": [{"role": "user", "content": complaint}]})

    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])

    response = result["messages"][-1].content
    tools_str = " -> ".join(tools_used) if tools_used else "No tools called"
    return response, tools_str


# ── Interface ─────────────────────────────────────────────────────────────────────────────

EXAMPLES = [
    "Why do demogorgons sometimes eat people and sometimes don't?",
    "The portal opens on different days - is there a schedule?",
    "Why can some psychics see the Downside Up and others can't?",
    "Why do creatures and power lines react so strangely together?",
]

with gr.Blocks(title="Becma - Downside-Up Complaint Bureau") as demo:
    gr.Markdown("# Becma - Downside-Up Complaint Bureau\n*Your official channel for Normal Objects universe inconsistencies*")

    with gr.Row():
        with gr.Column(scale=1):
            complaint_box = gr.Textbox(
                label="Your Complaint",
                placeholder="Why do demogorgons sometimes eat people and sometimes don't?",
                lines=4,
            )
            submit_btn = gr.Button("Submit Complaint", variant="primary")
            gr.Examples(examples=EXAMPLES, inputs=complaint_box, label="Sample Complaints")

        with gr.Column(scale=1):
            response_box = gr.Textbox(label="Becma's Response", lines=10, interactive=False)
            tools_box = gr.Textbox(label="Tools Used", lines=1, interactive=False)

    submit_btn.click(fn=handle_complaint, inputs=complaint_box, outputs=[response_box, tools_box])
    complaint_box.submit(fn=handle_complaint, inputs=complaint_box, outputs=[response_box, tools_box])

if __name__ == "__main__":
    demo.launch()
