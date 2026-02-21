"""
Quick test: Generate a blog post using the full pipeline.

Run from project root:
    python test_blog_post.py
"""

import sys
import os

# Add src/ to path so imports work
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from dotenv import load_dotenv
load_dotenv()

from knowledge_base import KnowledgeBase
from prompt_templates import PromptTemplates
from llm_integration import LLMIntegration


def main():
    # 1. Load knowledge base
    print("=" * 60)
    print("STEP 1: Loading knowledge base...")
    print("=" * 60)

    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
    kb = KnowledgeBase(kb_path)
    knowledge = kb.get_structured_knowledge()

    brand_voice = knowledge.get("brand_voice", "")
    product_info = knowledge.get("product_info", "")
    market_trends = knowledge.get("market_trends", "")
    past_content = knowledge.get("past_content", "")
    competitor_analysis = knowledge.get("competitor_analysis", "")

    print(f"  Loaded {len(knowledge)} knowledge sections")
    print(f"  Brand voice: {len(brand_voice)} chars")
    print(f"  Product info: {len(product_info)} chars")
    print(f"  Market trends: {len(market_trends)} chars")
    print(f"  Past content: {len(past_content)} chars")
    print(f"  Competitor analysis: {len(competitor_analysis)} chars")

    # 2. Generate the prompt — MoveAtlas-relevant topic
    print("\n" + "=" * 60)
    print("STEP 2: Building blog post prompt...")
    print("=" * 60)

    prompt = PromptTemplates.blog_post_template(
        brand_voice=brand_voice,
        product_info=product_info,
        market_trends=market_trends,
        topic="Why One Gym Will Never Be Enough: The Rise of Multi-Studio Fitness in Europe",
        target_audience="Urban professionals (25-45) in major European cities who are active but bored with their single-gym routine",
        audience_type="general",
        tone="thought_leadership",
        goals=[
            "Position MoveAtlas as the leader in flexible fitness",
            "Drive sign-ups from urban professionals exploring alternatives",
            "Differentiate from Urban Sports Club and ClassPass",
        ],
        target_keyword="multi-studio fitness membership Europe",
    )

    print(f"  Prompt length: {len(prompt)} chars")

    # 3. Send to LLM
    print("\n" + "=" * 60)
    print("STEP 3: Sending to LLM...")
    print("=" * 60)

    llm = LLMIntegration(provider="anthropic")

    print(f"  Provider: {llm.provider}")
    print(f"  Model: {llm.model}")
    print("  Generating... (this may take 15-30 seconds)\n")

    # Use auto-refine loop: generate → review → refine until score >= 8
    print("  Running auto-refine loop (target: 8/10)...\n")

    result = llm.generate_and_review(
        generation_prompt=prompt,
        review_prompt_fn=PromptTemplates.uniqueness_check_template,
        brand_voice=brand_voice,
        content_type="blog_post",
        max_iterations=3,
    )

    # 4. Print the final refined content
    print("=" * 60)
    print(f"FINAL BLOG POST (after {result['iterations']} iteration(s))")
    print("=" * 60)
    print(result["content"])

    # 5. Print the final review
    print("\n" + "=" * 60)
    print("FINAL REVIEW")
    print("=" * 60)
    print(result["review"])

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
