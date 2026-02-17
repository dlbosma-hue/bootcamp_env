"""
LLM API integration module.

Supports both OpenAI and Anthropic as providers. Each call wraps the user
prompt with a persistent system prompt that enforces brand-aligned,
anti-generic content creation across every generation.
"""

import os
import json
import time
import logging
from typing import Optional, Dict, List

from openai import OpenAI
import anthropic

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — injected into every LLM call
# ---------------------------------------------------------------------------
# This is the "personality layer" that sits above every template prompt.
# It primes the model to behave as a brand-aware content creator, not a
# generic assistant.

SYSTEM_PROMPT = """You are an expert AI content creator that produces unique, brand-aligned content.

CORE DIRECTIVES:
1. You NEVER produce generic AI-slop. Every piece you write could only come
   from the specific brand described in the prompt.
2. You treat the knowledge base context (brand voice, product info, market
   trends) as ground truth — reference it explicitly, don't paraphrase into
   generic statements.
3. You take clear positions. You are opinionated based on the brand identity
   and market data provided.
4. You write for humans, not algorithms. Your content should feel like it was
   written by a sharp, experienced human who deeply understands the brand.
5. When given a content structure, follow it precisely but make each section
   feel natural — not like a filled-in template.
6. You proactively avoid: cliche openings, corporate buzzwords without
   context, vague claims, and balanced-but-meaningless "on one hand / on the
   other hand" hedging.

OUTPUT RULES:
- Follow the requested format exactly (blog post, LinkedIn, email, etc.)
- Respect word count constraints
- Include all requested deliverables (SEO keywords, subject lines, hashtags, etc.)
- When asked for structured output (JSON), return valid JSON only
"""


class LLMIntegration:
    """
    Integration with OpenAI and Anthropic APIs for content generation.

    Wraps every call with a system prompt that enforces brand-aligned,
    anti-generic content creation.

    Usage:
        llm = LLMIntegration()                           # OpenAI (default)
        llm = LLMIntegration(provider="anthropic")        # Anthropic

        content = llm.generate_completion(prompt)
        structured = llm.generate_structured_output(prompt, schema)
        results = llm.batch_generate([prompt1, prompt2])
    """

    SUPPORTED_PROVIDERS = ("openai", "anthropic")

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: str = "openai",
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the LLM integration.

        Args:
            api_key: API key. Falls back to env vars (OPENAI_API_KEY / ANTHROPIC_API_KEY).
            model: Model name. Falls back to DEFAULT_MODEL env var or provider default.
            provider: "openai" or "anthropic".
            system_prompt: Override the default system prompt.
        """
        self.provider = provider.lower()
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Provider must be one of {self.SUPPORTED_PROVIDERS}")

        self.system_prompt = system_prompt or SYSTEM_PROMPT

        # --- Provider-specific setup ---
        if self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("DEFAULT_MODEL", "gpt-4o")
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-sonnet-4-5-20250929"
            self.client = anthropic.Anthropic(api_key=self.api_key)

        # Defaults from env
        self.default_max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.default_temperature = float(os.getenv("TEMPERATURE", "0.7"))

        logger.info(
            "LLMIntegration initialized — provider=%s model=%s",
            self.provider,
            self.model,
        )

    # ------------------------------------------------------------------
    # CORE: generate_completion
    # ------------------------------------------------------------------

    def generate_completion(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate a text completion from the LLM.

        This is the primary method used by the content pipeline.
        The system prompt is automatically prepended.

        Args:
            prompt: The full prompt string (from PromptTemplates).
            max_tokens: Max tokens for the response.
            temperature: Sampling temperature (0.0–1.0).

        Returns:
            The generated text content.
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature

        logger.info(
            "Generating completion — provider=%s model=%s tokens=%d temp=%.2f",
            self.provider,
            self.model,
            max_tokens,
            temperature,
        )

        if self.provider == "openai":
            return self._openai_completion(prompt, max_tokens, temperature)
        return self._anthropic_completion(prompt, max_tokens, temperature)

    def _openai_completion(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Call OpenAI Chat Completions API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        logger.info(
            "OpenAI response received — tokens_used=%s",
            response.usage.total_tokens if response.usage else "unknown",
        )
        return content

    def _anthropic_completion(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Call Anthropic Messages API with retry on overload."""
        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text
                logger.info(
                    "Anthropic response received — input_tokens=%s output_tokens=%s",
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )
                return content
            except anthropic.InternalServerError:
                wait = 10 * (attempt + 1)
                logger.warning("API overloaded, retrying in %ds (attempt %d/3)", wait, attempt + 1)
                print(f"  API overloaded, retrying in {wait}s...")
                time.sleep(wait)
        raise RuntimeError("Anthropic API overloaded after 3 retries")

    # ------------------------------------------------------------------
    # STRUCTURED OUTPUT
    # ------------------------------------------------------------------

    def generate_structured_output(
        self,
        prompt: str,
        schema: Dict,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict:
        """
        Generate structured (JSON) output conforming to a schema.

        Appends JSON formatting instructions to the prompt and parses
        the response into a Python dict.

        Args:
            prompt: The prompt string.
            schema: JSON schema the output should conform to.
            max_tokens: Max tokens for the response.
            temperature: Sampling temperature. Defaults to 0.3 for consistency.

        Returns:
            Parsed dict from the LLM's JSON response.
        """
        temperature = temperature if temperature is not None else 0.3

        structured_prompt = f"""{prompt}

RESPONSE FORMAT:
Return your response as valid JSON conforming to this schema:
{json.dumps(schema, indent=2)}

Return ONLY the JSON object, no markdown fences or explanation."""

        raw = self.generate_completion(structured_prompt, max_tokens, temperature)

        # Strip markdown fences if the model wraps in ```json ... ```
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove first line (```json) and last line (```)
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])

        return json.loads(cleaned)

    # ------------------------------------------------------------------
    # BATCH GENERATION
    # ------------------------------------------------------------------

    def batch_generate(
        self,
        prompts: List[str],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> List[str]:
        """
        Generate completions for multiple prompts sequentially.

        Args:
            prompts: List of prompt strings.
            max_tokens: Max tokens per response.
            temperature: Sampling temperature.

        Returns:
            List of generated text content, one per prompt.
        """
        results = []
        for i, prompt in enumerate(prompts):
            logger.info("Batch generation — prompt %d/%d", i + 1, len(prompts))
            result = self.generate_completion(prompt, max_tokens, temperature)
            results.append(result)
        return results

