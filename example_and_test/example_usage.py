"""
Example Usage Script - AI Content Creator

This script demonstrates how to use the prompt templates with your knowledge base
to generate unique, brand-aligned content.

Run this to see the templates in action!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.knowledge_base import KnowledgeBase
from templates.prompt_templates import (
    blog_post_thought_leadership,
    linkedin_post_insight,
    email_newsletter_value_first,
    uniqueness_check_prompt,
    content_brief_generator,
    integrate_knowledge_bases
)


def print_separator(title=""):
    """Print a nice separator."""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def main():
    print_separator("AI CONTENT CREATOR - PROMPT TEMPLATE DEMO")

    # Step 1: Load Knowledge Base
    print("📚 Step 1: Loading Knowledge Base...")
    kb = KnowledgeBase('knowledge_base')
    knowledge = kb.get_structured_knowledge()

    print(f"   ✓ Loaded {len(knowledge)} knowledge categories:")
    for key in knowledge.keys():
        content_preview = knowledge[key][:60].replace('\n', ' ')
        print(f"      - {key}: {content_preview}...")

    # Step 2: Show Knowledge Base Summary
    print("\n📊 Step 2: Knowledge Base Summary...")
    summary = kb.summarize_knowledge_base()
    print(f"   Total Documents: {summary['total_documents']}")
    print(f"   Total Words: {summary['total_words']}")
    print(f"   Primary Documents: {summary['primary']['document_count']}")
    print(f"   Secondary Documents: {summary['secondary']['document_count']}")

    # Step 3: Generate Different Prompt Examples
    print_separator("EXAMPLE 1: Blog Post (Thought Leadership)")

    blog_prompt = blog_post_thought_leadership(
        brand_voice=knowledge.get('brand_voice', ''),
        product_info=knowledge.get('product_info', ''),
        market_trends=knowledge.get('market_trends', ''),
        topic="The Hidden Cost of Generic AI Content",
        target_audience="Marketing Directors and Content Strategists"
    )

    print("Generated Prompt Preview (first 500 characters):")
    print("-" * 80)
    print(blog_prompt[:500] + "...")
    print("-" * 80)
    print(f"\nFull prompt length: {len(blog_prompt)} characters")
    print("This prompt would be sent to your LLM API (OpenAI/Anthropic)")

    # Example 2: LinkedIn Post
    print_separator("EXAMPLE 2: LinkedIn Post")

    linkedin_prompt = linkedin_post_insight(
        brand_voice=knowledge.get('brand_voice', ''),
        market_trends=knowledge.get('market_trends', ''),
        insight_topic="Why most AI-generated content looks the same (and how to fix it)"
    )

    print("Generated Prompt Preview (first 400 characters):")
    print("-" * 80)
    print(linkedin_prompt[:400] + "...")
    print("-" * 80)
    print(f"\nFull prompt length: {len(linkedin_prompt)} characters")

    # Example 3: Email Newsletter
    print_separator("EXAMPLE 3: Email Newsletter")

    email_prompt = email_newsletter_value_first(
        brand_voice=knowledge.get('brand_voice', ''),
        market_trends=knowledge.get('market_trends', ''),
        main_topic="Breaking free from AI content homogenization",
        subscriber_segment="Marketing professionals"
    )

    print("Generated Prompt Preview (first 400 characters):")
    print("-" * 80)
    print(email_prompt[:400] + "...")
    print("-" * 80)
    print(f"\nFull prompt length: {len(email_prompt)} characters")

    # Example 4: Content Brief
    print_separator("EXAMPLE 4: Content Brief Generator")

    brief_prompt = content_brief_generator(
        brand_voice=knowledge.get('brand_voice', ''),
        product_info=knowledge.get('product_info', ''),
        market_trends=knowledge.get('market_trends', ''),
        content_type="Tutorial Video",
        target_keyword="AI content creation"
    )

    print("Generated Prompt Preview (first 400 characters):")
    print("-" * 80)
    print(brief_prompt[:400] + "...")
    print("-" * 80)
    print(f"\nFull prompt length: {len(brief_prompt)} characters")

    # Example 5: Using Helper Function
    print_separator("EXAMPLE 5: Knowledge Base Integration Helper")

    primary_kb = {
        'brand_voice': knowledge.get('brand_voice', ''),
        'product_info': knowledge.get('product_info', ''),
    }

    secondary_kb = {
        'market_trends': knowledge.get('market_trends', ''),
        'competitor_analysis': knowledge.get('competitor_analysis', '')
    }

    integrated_context = integrate_knowledge_bases(
        primary_kb_content=primary_kb,
        secondary_kb_content=secondary_kb,
        content_goal="Create a comprehensive blog post series on AI content creation"
    )

    print("Integrated Knowledge Base Context Preview:")
    print("-" * 80)
    print(integrated_context[:500] + "...")
    print("-" * 80)
    print(f"\nFull context length: {len(integrated_context)} characters")
    print("\nThis structured context can be used with any template!")

    # Show Next Steps
    print_separator("NEXT STEPS")

    print("""
To actually generate content, you need to:

1. Set up your LLM API credentials:
   - Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file
   - Example: OPENAI_API_KEY=sk-your-key-here

2. Update src/llm_integration.py to call the API:

   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": prompt}]
   )

   content = response.choices[0].message.content

3. Run the full pipeline in src/content_pipeline.py

4. Compare outputs:
   - Generate content WITH templates + knowledge base
   - Generate content WITHOUT (basic ChatGPT prompt)
   - Show uniqueness difference for your presentation

5. Create examples for your demo:
   - Side-by-side comparison
   - Highlight specific differences
   - Show brand alignment

For more examples, see:
- templates/prompt_templates.py (full template code with docstrings)
- PROMPT_TEMPLATES_GUIDE.md (comprehensive usage guide)
""")

    print_separator("DEMO COMPLETE!")
    print("\n✨ Your prompt engineering templates are ready to use!")
    print("   Run this script anytime to see example prompts generated from your knowledge base.\n")


if __name__ == "__main__":
    main()
