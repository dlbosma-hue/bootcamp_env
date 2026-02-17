"""
Gradio web interface for MoveAtlas Blog Generator.

Run with:  python src/app.py
Opens at:  http://localhost:7860
"""

import sys
from pathlib import Path

# Ensure src/ is on the import path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import gradio as gr

from knowledge_base import KnowledgeBase
from llm_integration import LLMIntegration
from prompt_templates import (
    blog_post_brand_authority_engine,
    blog_post_industry_problem_solution_engine,
    blog_post_hybrid_strategic_engine,
    human_voice_rewrite_prompt,
)

# ---------------------------------------------------------------------------
# Load environment & knowledge base once at startup
# ---------------------------------------------------------------------------
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

BASE_PATH = Path(__file__).parent.parent
KB = KnowledgeBase(str(BASE_PATH / "knowledge_base"))
STRUCTURED_KB = KB.get_structured_knowledge()

# ---------------------------------------------------------------------------
# Angle presets — each has multiple topic options + operational objective
# ---------------------------------------------------------------------------
ANGLE_PRESETS = {
    "Travel-Inspired": {
        "topics": [
            "Why Your Fitness Routine Should Travel With You",
            "The Airport Gym Is Dead: How Global Memberships Replace Drop-In Culture",
            "What Frequent Flyers Know About Fitness That Homebodies Don't",
            "Hotel Gyms Are a Lie: Building a Real Workout Routine Across Time Zones",
        ],
        "objective": (
            "Drive sign-ups from frequent travelers by showing how MoveAtlas "
            "eliminates cross-city fitness friction. Motivate readers to start "
            "a membership or re-subscribe so they never miss a workout on the road."
        ),
        "kpi": "20% increase in sign-ups from travel-segment users",
    },
    "Business / Corporate": {
        "topics": [
            "The Business Case for Flexible Fitness Benefits",
            "Why Your Company's Gym Subsidy Is Wasting Money",
            "SME Wellness Programs Don't Need Enterprise Budgets",
            "Employee Retention Starts at the Gym (Just Not the One You Think)",
        ],
        "objective": (
            "Drive corporate and SME wellness sign-ups by positioning MoveAtlas "
            "as the simplest employee fitness benefit. Motivate HR decision-makers "
            "to sign up their teams or re-activate lapsed corporate accounts."
        ),
        "kpi": "15% increase in B2B partnership inquiries",
    },
    "Remote Work": {
        "topics": [
            "Remote Workers Are Redefining What a Gym Membership Means",
            "Your Gym Membership Doesn't Work From Home (But It Should)",
            "The Digital Nomad's Guide to Never Skipping Leg Day",
            "How Hybrid Work Broke the Traditional Gym Model",
        ],
        "objective": (
            "Target remote and hybrid professionals who work from different cities. "
            "Motivate them to sign up for a membership that moves with them, or "
            "re-subscribe if they cancelled a traditional gym."
        ),
        "kpi": "15% increase in monthly sign-ups from remote workers",
    },
    "Lifestyle / Wellness": {
        "topics": [
            "Why One Gym Will Never Be Enough for the Modern Athlete",
            "The Case Against Fitness Loyalty: Why Variety Beats Routine",
            "You Don't Need a Home Gym. You Need a Home Network.",
            "Boutique Fitness Is Booming. Annual Contracts Are Holding It Back.",
        ],
        "objective": (
            "Drive general consumer sign-ups by positioning variety and exploration "
            "as the future of fitness. Motivate readers to join MoveAtlas or "
            "re-subscribe to unlock 1,000+ studios."
        ),
        "kpi": "15% increase in monthly sign-ups",
    },
    "Studio Partner": {
        "topics": [
            "How Boutique Studios Are Filling Empty Classes Without Spending on Ads",
            "The Revenue Problem No One Talks About in Boutique Fitness",
            "Why the Best Studios Are Joining Networks Instead of Fighting Them",
            "Empty Mats, Full Rent: Solving the Boutique Studio Occupancy Crisis",
        ],
        "objective": (
            "Drive studio partner onboarding by showing real occupancy and revenue "
            "benefits. Motivate studio owners to sign up as MoveAtlas partners "
            "or re-activate their partnership."
        ),
        "kpi": "10% increase in new studio partner sign-ups",
    },
}

ANGLE_CHOICES = list(ANGLE_PRESETS.keys())
TEMPLATE_CHOICES = ["Brand Authority", "Industry Problem-Solution", "Hybrid Strategic"]
PROVIDER_CHOICES = ["Anthropic (Claude)", "OpenAI (GPT-4o)"]


# ---------------------------------------------------------------------------
# Helper: truncate text to N words
# ---------------------------------------------------------------------------
def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


# ---------------------------------------------------------------------------
# Core generation function
# ---------------------------------------------------------------------------
def generate_blog(angle, topic_choice, custom_topic, template, provider, temperature, max_tokens, target_audience):
    """Generate a blog post based on user selections."""

    # Resolve topic: custom > dropdown selection
    preset = ANGLE_PRESETS[angle]
    if custom_topic and custom_topic.strip():
        topic = custom_topic.strip()
    else:
        topic = topic_choice
    objective = preset["objective"]
    kpi = preset["kpi"]

    # Extract knowledge base sections
    brand_voice = _truncate(STRUCTURED_KB.get("brand_voice", ""), 300)
    product_info = _truncate(STRUCTURED_KB.get("product_info", ""), 300)
    past_content = _truncate(STRUCTURED_KB.get("past_content", ""), 200)
    market_trends = _truncate(STRUCTURED_KB.get("market_trends", ""), 300)
    competitor_analysis = _truncate(STRUCTURED_KB.get("competitor_analysis", ""), 300)
    industry_insights = _truncate(STRUCTURED_KB.get("industry_insights", ""), 250)

    # Build prompt based on selected template
    if template == "Brand Authority":
        prompt = blog_post_brand_authority_engine(
            brand_voice_section=brand_voice,
            product_specs_section=product_info,
            past_success_pattern_section=past_content,
            operational_objective=objective,
            kpi_target=kpi,
            topic=topic,
            target_audience=target_audience,
        )
        word_target = "1,200–1,500"

    elif template == "Industry Problem-Solution":
        prompt = blog_post_industry_problem_solution_engine(
            market_data_section=market_trends,
            industry_trends_section=industry_insights or market_trends,
            competitor_snapshot=competitor_analysis,
            brand_positioning_summary=brand_voice,
            operational_objective=objective,
            kpi_target=kpi,
            topic=topic,
            target_audience=target_audience,
        )
        word_target = "1,300–1,600"

    else:  # Hybrid Strategic
        prompt = blog_post_hybrid_strategic_engine(
            brand_voice_section=brand_voice,
            product_specs_section=product_info,
            partner_metrics_snapshot=past_content,
            market_data_snapshot=market_trends,
            industry_trends_snapshot=industry_insights or market_trends,
            competitor_snapshot=competitor_analysis,
            operational_objective=objective,
            kpi_target=kpi,
            topic=topic,
            target_audience=target_audience,
        )
        word_target = "1,400–1,800"

    # Resolve LLM provider
    prov = "anthropic" if "Anthropic" in provider else "openai"
    llm = LLMIntegration(provider=prov)

    # Pass 1: Generate raw draft
    raw_draft = llm.generate_completion(
        prompt,
        max_tokens=int(max_tokens),
        temperature=float(temperature),
    )

    # Pass 2: Rewrite for human voice (lower temp for precise editing)
    rewrite_prompt = human_voice_rewrite_prompt(raw_draft)
    content = llm.generate_completion(
        rewrite_prompt,
        max_tokens=int(max_tokens),
        temperature=max(float(temperature) - 0.1, 0.15),
    )

    # Word count
    word_count = len(content.split())
    status = f"Word count: {word_count} (target: {word_target})"

    # Save to file for download
    output_path = BASE_PATH / "output_blog_post.md"
    full_content = f"# {topic}\n\n{content}"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return content, status, str(output_path)


# ---------------------------------------------------------------------------
# Update topic dropdown when angle changes
# ---------------------------------------------------------------------------
def update_topics(angle):
    topics = ANGLE_PRESETS[angle]["topics"]
    return gr.update(choices=topics, value=topics[0])


# ---------------------------------------------------------------------------
# Build the Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="MoveAtlas Blog Generator") as app:

    gr.Markdown("# MoveAtlas Blog Generator")
    gr.Markdown(
        "Generate brand-aligned blog posts with built-in sign-up / re-subscribe CTA. "
        "Choose an angle, pick a topic, and hit **Generate**."
    )

    with gr.Row():
        with gr.Column(scale=1):
            angle = gr.Dropdown(
                choices=ANGLE_CHOICES,
                value=ANGLE_CHOICES[0],
                label="Blog Angle",
                info="Sets the objective and KPI automatically",
            )
            topic_choice = gr.Dropdown(
                choices=ANGLE_PRESETS[ANGLE_CHOICES[0]]["topics"],
                value=ANGLE_PRESETS[ANGLE_CHOICES[0]]["topics"][0],
                label="Topic",
                info="Pre-built topics for this angle",
            )
            custom_topic = gr.Textbox(
                label="Or Write Your Own Topic",
                placeholder="Leave blank to use the selected topic above",
            )
            template = gr.Radio(
                choices=TEMPLATE_CHOICES,
                value=TEMPLATE_CHOICES[0],
                label="Template",
            )
            provider = gr.Dropdown(
                choices=PROVIDER_CHOICES,
                value=PROVIDER_CHOICES[0],
                label="LLM Provider",
            )

            with gr.Accordion("Advanced Settings", open=False):
                temperature = gr.Slider(
                    minimum=0.1, maximum=1.0, value=0.4, step=0.05,
                    label="Temperature",
                    info="Lower = more rule-following, higher = more creative",
                )
                max_tokens = gr.Slider(
                    minimum=2000, maximum=8000, value=4096, step=256,
                    label="Max Tokens",
                )
                target_audience = gr.Textbox(
                    value="Urban professionals (25-50) worldwide",
                    label="Target Audience",
                )

            generate_btn = gr.Button("Generate Blog Post", variant="primary", size="lg")

        with gr.Column(scale=2):
            output_md = gr.Markdown(label="Generated Blog Post")
            word_count_display = gr.Textbox(label="Status", interactive=False)
            download_path = gr.File(label="Download Blog Post")

    # Wire events
    angle.change(fn=update_topics, inputs=angle, outputs=topic_choice)

    generate_btn.click(
        fn=generate_blog,
        inputs=[angle, topic_choice, custom_topic, template, provider, temperature, max_tokens, target_audience],
        outputs=[output_md, word_count_display, download_path],
    )


if __name__ == "__main__":
    app.launch(share=True, theme=gr.themes.Soft())
