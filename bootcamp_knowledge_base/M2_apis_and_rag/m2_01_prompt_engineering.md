# LAB M2.01 - Prompt Engineering

## Use Case
Systematically improve prompts through three iterations (v1, v2, v3) across three tasks: sentiment analysis, product description generation, and data extraction. Goal: go from inconsistent outputs to production-ready consistency.

## The Three Tasks
1. Sentiment analysis - classify text as positive, negative, or neutral
2. Product description - generate marketing copy from a product name and category
3. Data extraction - pull structured fields (name, price, date) from unstructured text

## The Three Versions
- v1: Minimal prompt, no constraints. Establishes a baseline. Output is inconsistent.
- v2: Explicit format rules, output constraints, told exactly what to return.
- v3: Few-shot examples added. Chain-of-thought reasoning added for complex tasks.

## Results Achieved
- Sentiment analysis consistency: 0% (v1) to 95% (v3)
- Product description consistency: 0% (v1) to 85% (v3)
- Data extraction consistency: 53% (v1) to 95% (v3)
- Overall average improvement: 73.9%

## Key Prompt Engineering Techniques Used
- Be explicit: state the exact output format required
- Use positive framing: say what TO do, not just what NOT to do
- Few-shot examples: show 2-3 examples of ideal input/output pairs
- Chain-of-Thought: ask the model to reason step by step before giving the final answer
- XML tags: use tags like `<output>` to separate the answer from the reasoning

## Key Learning
The biggest jump in consistency comes from v1 to v2 (adding format rules). Few-shot examples in v3 help with edge cases and ambiguous inputs but are less impactful than format constraints alone.

## Submission
Jupyter notebook with all three versions tested at least 5 times each, consistency scores documented, and a reflection explaining which technique had the most impact.
