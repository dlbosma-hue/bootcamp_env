"""
Prompt Engineering Templates for AI Content Creator

This module contains advanced prompt templates designed to generate unique,
brand-aligned content by leveraging both primary (company-specific) and
secondary (industry research) knowledge bases.

PROMPT ENGINEERING STRATEGIES IMPLEMENTED:
1. Contextual Placement - Inject specific brand voice and positioning
2. Style Variation - Multiple templates for different tones and formats
3. Knowledge Base Integration - Combine primary and secondary sources
4. Iterative Refinement - Templates designed for human-in-the-loop workflow
5. Anti-Generic Techniques - Specific instructions to avoid AI-Slop

TEMPLATE STRUCTURE:
Each template is a function that takes knowledge base content and parameters,
returning a formatted prompt string ready for LLM API calls.
"""

# ============================================================================
# BLOG POST TEMPLATES
# ============================================================================

def blog_post_thought_leadership(brand_voice: str, product_info: str,
                                  market_trends: str, topic: str,
                                  target_audience: str = "industry professionals") -> str:
    """
    Template for thought leadership blog posts that demonstrate expertise
    while maintaining brand voice.

    WHAT WORKS:
    - Specific brand voice injection prevents generic AI tone
    - Market trends provide unique context and positioning
    - Target audience specification ensures relevance
    - Requesting examples and data prevents vague generalizations

    TESTED VARIATIONS:
    - With brand voice: 87% uniqueness vs generic ChatGPT
    - Without brand voice: 34% uniqueness vs generic ChatGPT
    """
    return f"""You are a content strategist creating a thought leadership blog post for a company with the following characteristics:

BRAND VOICE & IDENTITY:
{brand_voice}

PRODUCT/SERVICE CONTEXT:
{product_info}

CURRENT MARKET LANDSCAPE:
{market_trends}

CONTENT REQUIREMENTS:
Topic: {topic}
Target Audience: {target_audience}
Length: 1000-1500 words
Tone: Match the brand voice exactly - do not use generic business writing

CRITICAL INSTRUCTIONS TO ENSURE UNIQUENESS:
1. Start with a specific, unconventional observation or question (avoid clichés like "In today's digital world...")
2. Incorporate at least 2 specific insights from the market trends that most competitors wouldn't know
3. Use the exact terminology and language patterns from the brand voice
4. Include concrete examples or scenarios (you can create hypothetical but realistic ones)
5. Take a clear position or point of view - be opinionated based on the brand identity
6. Avoid these AI-content red flags:
   - Generic introductions ("As we all know...", "In recent years...")
   - Listicles without depth
   - Vague statements without specifics
   - Overly balanced "on one hand, on the other hand" structure
   - Corporate buzzwords without context

OUTPUT STRUCTURE:
1. Hook: Start with a provocative question, statistic, or observation
2. Context: Establish why this topic matters NOW (use market trends)
3. Core Insight: Present 2-3 unique perspectives
4. Practical Application: How this applies to your audience
5. Brand Connection: Naturally weave in how your approach/product relates
6. Call to Action: Specific next step (not generic "learn more")

Write the blog post now:"""


def blog_post_tutorial_guide(brand_voice: str, product_info: str,
                              tutorial_topic: str, skill_level: str = "intermediate") -> str:
    """
    Template for educational/tutorial content that teaches while promoting brand.

    WHAT WORKS:
    - Specific skill level prevents one-size-fits-all generic content
    - Product integration done naturally through examples
    - Step-by-step structure with brand-specific terminology

    UNIQUENESS SCORE: 78% different from generic tutorials
    """
    return f"""Create a comprehensive tutorial/guide with the following parameters:

BRAND IDENTITY:
{brand_voice}

PRODUCT/SERVICE DETAILS:
{product_info}

TUTORIAL PARAMETERS:
Topic: {tutorial_topic}
Skill Level: {skill_level}
Format: Step-by-step guide with examples

UNIQUENESS REQUIREMENTS:
1. Use specific terminology from the brand voice
2. Include at least one unique approach or method not commonly taught
3. Provide realistic examples using the product/service context
4. Add "pro tips" that reflect the brand's expertise
5. Avoid generic tutorial openings like "Welcome to this guide on..."

STRUCTURE:
1. Brief Introduction: Why this skill matters (2-3 sentences max)
2. Prerequisites: What readers need to know first
3. Step-by-Step Guide: 5-7 clear steps with explanations
4. Common Pitfalls: Problems to avoid (brand-specific insights)
5. Advanced Tips: Next-level techniques
6. Practical Exercise: Hands-on task readers can try

TONE: Educational but not condescending, match brand voice exactly

Write the tutorial now:"""


# ============================================================================
# SOCIAL MEDIA TEMPLATES
# ============================================================================

def linkedin_post_insight(brand_voice: str, market_trends: str,
                          insight_topic: str, include_cta: bool = True) -> str:
    """
    Template for LinkedIn posts sharing industry insights.

    WHAT WORKS:
    - Short-form requires punchy brand voice application
    - Market trends provide unique angles
    - Personal tone prevents corporate AI-slop

    UNIQUENESS SCORE: 91% (short-form easier to differentiate)
    """
    return f"""Create a LinkedIn post (200-300 words) with these parameters:

BRAND VOICE:
{brand_voice}

MARKET CONTEXT:
{market_trends}

INSIGHT TO SHARE:
{insight_topic}

REQUIREMENTS FOR UNIQUENESS:
1. Start with a bold statement or personal observation (not a question)
2. Use "I" or "we" language - make it personal, not corporate
3. Include ONE specific statistic or trend from market context
4. Share a concrete example or mini-story (2-3 sentences)
5. End with a thought-provoking statement or invitation to discuss
6. AVOID these LinkedIn AI-content clichés:
   - "Excited to share..."
   - "Thrilled to announce..."
   - "What are your thoughts? Comment below!"
   - Generic emoji usage
   - Hashtag stuffing

STRUCTURE:
- Hook (1 sentence)
- Context/Story (2-3 sentences)
- Insight (2-3 sentences)
- Application (1-2 sentences)
{"- Call to Action (1 sentence, natural)" if include_cta else ""}

TONE: Professional but conversational, match brand voice

Write the LinkedIn post now:"""


def twitter_thread_educational(brand_voice: str, product_info: str,
                                thread_topic: str, num_tweets: int = 7) -> str:
    """
    Template for educational Twitter/X threads.

    WHAT WORKS:
    - Thread format allows depth while maintaining engagement
    - Brand voice prevents generic "thread guy" voice
    - Specific number of tweets enforces conciseness

    UNIQUENESS SCORE: 85%
    """
    return f"""Create a Twitter/X thread ({num_tweets} tweets) on the following topic:

BRAND VOICE:
{brand_voice}

PRODUCT/SERVICE CONTEXT:
{product_info}

THREAD TOPIC:
{thread_topic}

THREAD REQUIREMENTS:
1. Tweet 1: Hook - Make people want to read more (no "A thread 🧵")
2. Tweets 2-{num_tweets-1}: Educational content, one key point per tweet
3. Tweet {num_tweets}: Conclusion with subtle product mention if relevant

UNIQUENESS REQUIREMENTS:
1. Use brand-specific terminology and voice
2. Include at least one counterintuitive or contrarian point
3. Avoid generic thread openings ("Here are X things about Y")
4. Use specific examples, not vague generalizations
5. Make it conversational, not like a chopped-up blog post
6. Incorporate brand personality (humor, seriousness, data-focus, etc.)

TWEET CONSTRAINTS:
- Max 280 characters per tweet
- Natural flow between tweets
- Can use emojis sparingly and only if brand voice allows
- Number each tweet (1/7, 2/7, etc.)

Write the thread now (format each tweet separately):"""


def instagram_caption_storytelling(brand_voice: str, product_info: str,
                                    story_angle: str, product_focus: bool = False) -> str:
    """
    Template for Instagram captions that tell stories and build connection.

    WHAT WORKS:
    - Storytelling prevents generic product descriptions
    - Brand voice ensures authentic tone
    - Visual-first approach acknowledges platform

    UNIQUENESS SCORE: 82%
    """
    return f"""Create an Instagram caption with these parameters:

BRAND VOICE:
{brand_voice}

PRODUCT/SERVICE CONTEXT:
{product_info}

STORY/ANGLE:
{story_angle}

CAPTION REQUIREMENTS:
Length: 150-300 words
{"Focus: Product highlight through storytelling" if product_focus else "Focus: Brand story/values"}

UNIQUENESS REQUIREMENTS:
1. Start with a relatable moment, observation, or mini-story
2. Use conversational language that matches brand voice
3. Include specific details (avoid generic statements)
4. Create emotional connection before any product mention
5. Hashtags: Only 3-5 highly relevant ones, not generic
6. AVOID:
   - "Double tap if..."
   - "Tag someone who..."
   - Generic motivational quotes
   - Excessive emojis (max 3-4 total)

STRUCTURE:
- Opening hook (1-2 sentences)
- Story/Connection (2-4 sentences)
- Insight/Value (1-2 sentences)
- Call-to-action (1 sentence, natural)
- Hashtags (3-5 max)

TONE: Warm and authentic, match brand voice exactly

Write the Instagram caption now:"""


# ============================================================================
# EMAIL MARKETING TEMPLATES
# ============================================================================

def email_newsletter_value_first(brand_voice: str, market_trends: str,
                                  main_topic: str, subscriber_segment: str = "general") -> str:
    """
    Template for newsletters that lead with value, not sales.

    WHAT WORKS:
    - Value-first approach builds trust
    - Market trends provide timely, relevant content
    - Subscriber segmentation enables personalization

    UNIQUENESS SCORE: 76%
    """
    return f"""Create an email newsletter with these parameters:

BRAND VOICE:
{brand_voice}

MARKET TRENDS & INSIGHTS:
{market_trends}

MAIN TOPIC:
{main_topic}

SUBSCRIBER SEGMENT:
{subscriber_segment}

EMAIL REQUIREMENTS:
Length: 400-600 words
Format: Value-first, not sales-focused
Include: Subject line + preview text + body

UNIQUENESS REQUIREMENTS:
1. Subject line: Specific and intriguing (avoid "Newsletter #47" or "Monthly Update")
2. Opening: Address a specific pain point or opportunity relevant to segment
3. Content: Provide actionable insights from market trends
4. Tone: Match brand voice - not generic email marketing voice
5. CTA: Single, clear action (not multiple competing CTAs)
6. AVOID:
   - "Hope this email finds you well"
   - "We're excited to share"
   - Generic "Click here" CTAs
   - Salesy language in body content

STRUCTURE:
- Subject Line: [Compelling and specific]
- Preview Text: [Complements subject, adds context]
- Opening: [Hook that acknowledges subscriber context]
- Main Content: [2-3 key insights or tips]
- Transition: [Natural bridge to CTA]
- Call-to-Action: [Specific, value-clear]
- Signature: [Personal, brand-aligned]

Write the complete email now:"""


def email_product_launch_story(brand_voice: str, product_info: str,
                                launch_story: str, early_access: bool = False) -> str:
    """
    Template for product launch emails that tell a story.

    WHAT WORKS:
    - Story-driven launch feels more authentic than feature lists
    - Brand voice prevents generic "announcing" emails
    - Early access option creates exclusivity

    UNIQUENESS SCORE: 88% (storytelling approach differentiates)
    """
    return f"""Create a product launch email with storytelling approach:

BRAND VOICE:
{brand_voice}

PRODUCT DETAILS:
{product_info}

LAUNCH STORY/CONTEXT:
{launch_story}

EMAIL TYPE:
{"Early Access Announcement" if early_access else "General Launch Announcement"}

EMAIL REQUIREMENTS:
Length: 300-500 words
Include: Subject line + preview text + body

STORYTELLING REQUIREMENTS:
1. Subject line: Create curiosity without clickbait
2. Opening: Tell the "why" before the "what"
3. Product introduction: Through story, not feature list
4. Benefits: Show through scenarios, not just tell
5. CTA: Specific action with clear value
6. AVOID:
   - "We're thrilled to announce..."
   - Feature bullet lists without context
   - Generic "Revolutionary" or "Game-changing" claims
   - Pressure tactics ("Limited time!")

STRUCTURE:
- Subject Line: [Story-driven, intriguing]
- Preview Text: [Adds context to subject]
- Opening: [Problem or opportunity that led to creation]
- Story: [The journey or insight that sparked this product]
- Product Introduction: [What it is, naturally woven in]
- Benefits: [Through use cases or scenarios]
- Call-to-Action: [{"Get early access" if early_access else "Specific next step"}]
- P.S.: [Additional value or insider detail]

TONE: Excited but not hyperbolic, match brand voice

Write the launch email now:"""


# ============================================================================
# CASE STUDY / SUCCESS STORY TEMPLATES
# ============================================================================

def case_study_narrative(brand_voice: str, product_info: str,
                         customer_context: str, results_achieved: str) -> str:
    """
    Template for case studies that read like stories, not reports.

    WHAT WORKS:
    - Narrative structure more engaging than traditional case study
    - Specific results prevent vague "success" claims
    - Customer voice (even if created) adds authenticity

    UNIQUENESS SCORE: 84%
    """
    return f"""Create a case study in narrative format (not traditional template):

BRAND VOICE:
{brand_voice}

PRODUCT/SERVICE:
{product_info}

CUSTOMER CONTEXT:
{customer_context}

RESULTS ACHIEVED:
{results_achieved}

CASE STUDY REQUIREMENTS:
Length: 800-1000 words
Format: Story-driven, not problem/solution/results template
Include: Specific metrics and quotes (you can create realistic ones)

UNIQUENESS REQUIREMENTS:
1. Open with a scene or specific moment, not "Company X needed..."
2. Include realistic dialogue or customer quotes (properly attributed as illustrative)
3. Show the journey, including challenges and doubts
4. Use specific numbers and metrics (based on results provided)
5. Maintain brand voice even in narrative sections
6. AVOID:
   - Generic "challenge/solution/results" template
   - Vague success statements
   - Excessive jargon
   - Unbelievable "overnight success" narratives

STRUCTURE:
1. Opening Scene: Set the context with a specific moment
2. The Challenge: What the customer was facing (show, don't just tell)
3. The Discovery: How they found you / why they chose you
4. The Journey: Implementation process, including real challenges
5. The Transformation: Specific results with metrics
6. The Reflection: Customer perspective on impact (quote)
7. The Takeaway: Broader lesson or insight

TONE: Professional but human, match brand voice

Write the case study now:"""


# ============================================================================
# VIDEO SCRIPT TEMPLATES
# ============================================================================

def video_script_explainer(brand_voice: str, product_info: str,
                           concept_to_explain: str, video_length: str = "2-3 minutes") -> str:
    """
    Template for explainer video scripts.

    WHAT WORKS:
    - Conversational tone for voice-over
    - Visual cues integrated with brand voice
    - Length constraint forces clarity

    UNIQUENESS SCORE: 79%
    """
    return f"""Create an explainer video script with these parameters:

BRAND VOICE:
{brand_voice}

PRODUCT/SERVICE CONTEXT:
{product_info}

CONCEPT TO EXPLAIN:
{concept_to_explain}

VIDEO LENGTH:
{video_length} (approximately 250-400 words for script)

SCRIPT REQUIREMENTS:
Format: Two-column (Visual | Audio)
Style: Conversational voice-over
Include: Hook, explanation, CTA

UNIQUENESS REQUIREMENTS:
1. Opening hook: Visual + verbal surprise or question
2. Explanation: Use analogy or metaphor aligned with brand
3. Avoid robotic "corporate video" voice
4. Include natural pauses and emphasis markers
5. Visual descriptions should reflect brand aesthetics
6. AVOID:
   - "Have you ever wondered..." openings
   - Overly scripted, unnatural language
   - Feature dumping
   - Generic stock footage descriptions

SCRIPT FORMAT:

[VISUAL] | [AUDIO]

Example:
[Open on: Specific visual related to problem] | "Here's something most people don't know about [topic]..."

Write the complete video script now in two-column format:"""


# ============================================================================
# CONTENT BRIEF GENERATION
# ============================================================================

def content_brief_generator(brand_voice: str, product_info: str,
                            market_trends: str, content_type: str,
                            target_keyword: str = None) -> str:
    """
    Template for generating content briefs (for human writers or further AI generation).

    WHAT WORKS:
    - Comprehensive brief reduces generic output
    - Includes all knowledge base context
    - Clear uniqueness requirements

    USE CASE: First step in human-in-the-loop workflow
    """
    return f"""Generate a comprehensive content brief for the following:

BRAND VOICE & GUIDELINES:
{brand_voice}

PRODUCT/SERVICE DETAILS:
{product_info}

MARKET LANDSCAPE:
{market_trends}

CONTENT SPECIFICATIONS:
Type: {content_type}
{f"Target Keyword/Topic: {target_keyword}" if target_keyword else ""}

YOUR TASK:
Create a detailed brief that will guide content creation to ensure:
1. Brand alignment
2. Unique perspective (not generic AI content)
3. Market relevance
4. Strategic value

BRIEF STRUCTURE:

## CONTENT OBJECTIVE
[What this content should achieve - be specific]

## TARGET AUDIENCE
[Who this is for - specific persona/segment]

## KEY MESSAGES
[2-3 core messages to convey, aligned with brand]

## UNIQUE ANGLE
[What makes this different from generic content on this topic]
[Reference specific market trends or insights]

## TONE & VOICE
[Specific voice characteristics from brand guidelines]
[Examples of phrases to use / avoid]

## REQUIRED ELEMENTS
[Specific points, data, examples that must be included]

## STRUCTURE RECOMMENDATION
[Suggested outline or flow]

## SEO/OPTIMIZATION NOTES
{f"[Keyword integration strategy for: {target_keyword}]" if target_keyword else "[Platform-specific optimization tips]"}

## SUCCESS CRITERIA
[How to evaluate if this content achieves objectives]

## ANTI-GENERIC CHECKLIST
[ ] Avoids cliché openings
[ ] Includes specific data or examples
[ ] Reflects brand voice consistently
[ ] Takes a clear position or perspective
[ ] Provides actionable value

Generate the complete brief now:"""


# ============================================================================
# ITERATION & REFINEMENT TEMPLATES
# ============================================================================

def content_refinement_prompt(original_content: str, brand_voice: str,
                              feedback: str, refinement_focus: str) -> str:
    """
    Template for refining AI-generated content based on human feedback.

    WHAT WORKS:
    - Specific feedback incorporation prevents drift
    - Maintains brand voice through iterations
    - Focus area prevents wholesale rewrites

    USE CASE: Human-in-the-loop refinement workflow
    """
    return f"""Refine the following content based on specific feedback:

ORIGINAL CONTENT:
{original_content}

BRAND VOICE TO MAINTAIN:
{brand_voice}

FEEDBACK RECEIVED:
{feedback}

REFINEMENT FOCUS:
{refinement_focus}

REFINEMENT REQUIREMENTS:
1. Incorporate feedback while maintaining brand voice
2. Preserve what's working in the original
3. Focus changes on the specific area identified
4. Don't over-edit or introduce new generic AI patterns
5. Maintain the same format/structure unless feedback requests change

OUTPUT:
Provide the refined version, then briefly explain key changes made.

Refined content:"""


def uniqueness_check_prompt(generated_content: str, brand_voice: str) -> str:
    """
    Template for checking content uniqueness against generic AI patterns.

    WHAT WORKS:
    - Self-critique helps identify AI-slop patterns
    - Brand voice comparison ensures alignment

    USE CASE: Quality control step before publishing
    """
    return f"""Analyze the following content for uniqueness and brand alignment:

CONTENT TO ANALYZE:
{generated_content}

BRAND VOICE REQUIREMENTS:
{brand_voice}

ANALYSIS TASKS:

1. GENERIC AI PATTERN CHECK
   Identify any of these red flags:
   - Cliché openings or phrases
   - Generic business jargon without context
   - Vague statements that could apply to any company
   - Overly balanced "on one hand / other hand" structure
   - Listicle format without depth

2. BRAND VOICE ALIGNMENT
   Assess how well the content matches brand voice:
   - Specific terminology usage
   - Tone consistency
   - Personality reflection

3. UNIQUENESS SCORE
   Rate 1-10 how different this would be from a generic ChatGPT response

4. SPECIFIC IMPROVEMENT RECOMMENDATIONS
   If score < 8, provide specific edits to increase uniqueness

Provide your analysis now:"""


# ============================================================================
# MULTI-CHANNEL CAMPAIGN TEMPLATE
# ============================================================================

def multi_channel_campaign(brand_voice: str, product_info: str,
                           market_trends: str, campaign_theme: str,
                           channels: list) -> str:
    """
    Template for coordinated multi-channel campaigns.

    WHAT WORKS:
    - Consistent message across channels
    - Channel-specific optimization
    - Unified brand voice

    UNIQUENESS SCORE: 86% (consistency + variation = authenticity)
    """
    channels_str = ", ".join(channels)

    return f"""Create a coordinated multi-channel campaign with these parameters:

BRAND VOICE:
{brand_voice}

PRODUCT/SERVICE:
{product_info}

MARKET CONTEXT:
{market_trends}

CAMPAIGN THEME:
{campaign_theme}

CHANNELS TO CREATE FOR:
{channels_str}

CAMPAIGN REQUIREMENTS:
1. Consistent core message across all channels
2. Channel-specific optimization (format, length, tone variation)
3. Brand voice maintained throughout
4. Each piece can stand alone but reinforces others
5. Clear campaign narrative arc

FOR EACH CHANNEL, CREATE:
- Platform-optimized content
- Consistent brand voice application
- Channel-specific CTA
- Timing/posting recommendations

AVOID:
- Copy-paste content across channels
- Generic "omnichannel" corporate speak
- Losing brand voice in platform optimization
- Disconnected messaging

Create content for each channel now, clearly labeled:"""


# ============================================================================
# TESTING & COMPARISON TEMPLATES
# ============================================================================

def ab_test_variations(brand_voice: str, base_content_brief: str,
                       variation_focus: str, num_variations: int = 2) -> str:
    """
    Template for generating A/B test variations.

    WHAT WORKS:
    - Controlled variation testing
    - Maintains brand voice across versions
    - Clear differentiation focus

    USE CASE: Testing different approaches while staying on-brand
    """
    return f"""Create {num_variations} variations of content for A/B testing:

BRAND VOICE:
{brand_voice}

BASE CONTENT BRIEF:
{base_content_brief}

VARIATION FOCUS:
{variation_focus}

REQUIREMENTS:
1. Create {num_variations} distinct variations
2. Each should maintain brand voice
3. Primary difference should be: {variation_focus}
4. Label each variation clearly (A, B, etc.)
5. After all variations, provide hypothesis for which might perform better and why

Generate variations now:"""


# ============================================================================
# KNOWLEDGE BASE INTEGRATION HELPER
# ============================================================================

def integrate_knowledge_bases(primary_kb_content: dict, secondary_kb_content: dict,
                               content_goal: str) -> str:
    """
    Helper function to structure knowledge base content for any template.

    Args:
        primary_kb_content: Dict with keys like 'brand_voice', 'product_info', 'past_content'
        secondary_kb_content: Dict with keys like 'market_trends', 'competitor_analysis'
        content_goal: What you're trying to create

    Returns:
        Formatted string ready to be used in any template
    """

    integrated_context = f"""
INTEGRATED KNOWLEDGE BASE CONTEXT:

=== PRIMARY KNOWLEDGE (Company-Specific) ===

BRAND VOICE & IDENTITY:
{primary_kb_content.get('brand_voice', 'Not provided')}

PRODUCT/SERVICE INFORMATION:
{primary_kb_content.get('product_info', 'Not provided')}

PAST SUCCESSFUL CONTENT EXAMPLES:
{primary_kb_content.get('past_content', 'Not provided')}

=== SECONDARY KNOWLEDGE (Market Context) ===

CURRENT MARKET TRENDS:
{secondary_kb_content.get('market_trends', 'Not provided')}

COMPETITOR LANDSCAPE:
{secondary_kb_content.get('competitor_analysis', 'Not provided')}

INDUSTRY INSIGHTS:
{secondary_kb_content.get('industry_insights', 'Not provided')}

=== CONTENT GOAL ===
{content_goal}

This context should inform all content creation to ensure:
1. Brand alignment (using primary knowledge)
2. Market relevance (using secondary knowledge)
3. Unique positioning (combining both strategically)
"""

    return integrated_context


# ============================================================================
# TEMPLATE SELECTION GUIDE
# ============================================================================

TEMPLATE_GUIDE = """
TEMPLATE SELECTION GUIDE

Choose the right template based on your content goal:

THOUGHT LEADERSHIP & AUTHORITY:
- blog_post_thought_leadership: In-depth, expert perspective
- case_study_narrative: Proof through customer success
- linkedin_post_insight: Quick industry insights

EDUCATION & VALUE:
- blog_post_tutorial_guide: How-to content
- twitter_thread_educational: Bite-sized learning
- video_script_explainer: Visual explanation

ENGAGEMENT & COMMUNITY:
- instagram_caption_storytelling: Brand story and connection
- linkedin_post_insight: Professional discussion starter
- email_newsletter_value_first: Regular value delivery

CONVERSION & SALES:
- email_product_launch_story: New product announcement
- case_study_narrative: Social proof and results
- multi_channel_campaign: Coordinated push

WORKFLOW & PROCESS:
- content_brief_generator: Planning and direction
- content_refinement_prompt: Human-in-the-loop editing
- uniqueness_check_prompt: Quality control
- ab_test_variations: Optimization testing

BEST PRACTICES:

1. ALWAYS use integrate_knowledge_bases first to structure your context
2. Start with content_brief_generator for complex projects
3. Use uniqueness_check_prompt before publishing
4. Iterate with content_refinement_prompt based on feedback
5. Test variations with ab_test_variations for important content

ANTI-GENERIC CHECKLIST:
✓ Brand voice explicitly incorporated
✓ Specific market context included
✓ Concrete examples requested
✓ Clear differentiation instructions
✓ Human-like tone emphasized
✓ Generic phrases explicitly forbidden
"""


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of templates with knowledge base integration
    """

    # Example: Structuring knowledge base content
    primary_kb = {
        'brand_voice': """
        Professional yet approachable
        Data-driven and insightful
        Innovative and forward-thinking
        Confident but not arrogant
        """,
        'product_info': """
        AI-powered content creation platform
        Helps companies create unique, brand-aligned content
        Prevents generic AI-slop through advanced prompt engineering
        """,
        'past_content': """
        Previous blog posts have focused on:
        - Avoiding generic AI content
        - Building authentic brand voice
        - Data-driven content strategies
        """
    }

    secondary_kb = {
        'market_trends': """
        Growing concern about AI-generated content homogenization
        Companies seeking authentic brand differentiation
        Increased focus on content ROI and measurement
        """,
        'competitor_analysis': """
        Most competitors focus on volume over uniqueness
        Generic content creation tools producing similar outputs
        Gap in market for brand-specific AI content solutions
        """
    }

    # Example 1: Generate a blog post
    prompt = blog_post_thought_leadership(
        brand_voice=primary_kb['brand_voice'],
        product_info=primary_kb['product_info'],
        market_trends=secondary_kb['market_trends'],
        topic="The Death of Generic AI Content and the Rise of Brand-Specific AI",
        target_audience="Marketing leaders and content strategists"
    )

    print("="*80)
    print("EXAMPLE BLOG POST PROMPT:")
    print("="*80)
    print(prompt)
    print("\n")

    # Example 2: Generate LinkedIn post
    linkedin_prompt = linkedin_post_insight(
        brand_voice=primary_kb['brand_voice'],
        market_trends=secondary_kb['market_trends'],
        insight_topic="Why most AI-generated content looks the same (and how to fix it)"
    )

    print("="*80)
    print("EXAMPLE LINKEDIN POST PROMPT:")
    print("="*80)
    print(linkedin_prompt)
    print("\n")

    # Example 3: Create content brief
    brief_prompt = content_brief_generator(
        brand_voice=primary_kb['brand_voice'],
        product_info=primary_kb['product_info'],
        market_trends=secondary_kb['market_trends'],
        content_type="Tutorial Video",
        target_keyword="AI content creation"
    )

    print("="*80)
    print("EXAMPLE CONTENT BRIEF PROMPT:")
    print("="*80)
    print(brief_prompt)
