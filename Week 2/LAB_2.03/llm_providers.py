"""LLM provider integration with fallback support."""
import os
import time
import random
import tiktoken
from openai import OpenAI
from anthropic import Anthropic
from config import Config

# Pricing (per million tokens)
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00}
}

class CostTracker:
    """Track API costs."""
    
    def __init__(self):
        self.total_cost = 0.0
        self.requests = []
    
    def track_request(self, provider, model, input_tokens, output_tokens):
        """Track a single request."""
        pricing = PRICING.get(model, {"input": 3.0, "output": 15.0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        cost = input_cost + output_cost
        
        self.total_cost += cost
        self.requests.append({
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })
        
        return cost
    
    def get_summary(self):
        """Get cost summary."""
        total_input = sum(r["input_tokens"] for r in self.requests)
        total_output = sum(r["output_tokens"] for r in self.requests)
        
        return {
            "total_requests": len(self.requests),
            "total_cost": self.total_cost,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "average_cost": self.total_cost / max(len(self.requests), 1)
        }
    
    def check_budget(self, daily_budget):
        """Check if we're within budget."""
        if self.total_cost >= daily_budget:
            raise Exception(f"Daily budget of ${daily_budget:.2f} exceeded! Current: ${self.total_cost:.2f}")
        
        percent_used = (self.total_cost / daily_budget) * 100
        if percent_used >= 90:
            print(f"⚠️  Warning: {percent_used:.1f}% of daily budget used")

def count_tokens(text, model="gpt-4o-mini"):
    """Count tokens in text."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: estimate 4 characters per token
        return len(text) // 4

class LLMProviders:
    """Manage multiple LLM providers with fallback."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.cost_tracker = CostTracker()
        
        # Rate limiting
        self.openai_last_call = 0
        self.anthropic_last_call = 0
        self.openai_interval = 60.0 / Config.OPENAI_RPM
        self.anthropic_interval = 60.0 / Config.ANTHROPIC_RPM
    
    def _wait_openai(self):
        """Rate limit OpenAI calls with jitter for better distribution."""
        elapsed = time.time() - self.openai_last_call
        if elapsed < self.openai_interval:
            jitter = random.uniform(0, self.openai_interval * 0.2)
            wait_time = (self.openai_interval - elapsed) + jitter
            time.sleep(wait_time)
        self.openai_last_call = time.time()

    def _wait_anthropic(self):
        """Rate limit Anthropic calls with jitter for better distribution."""
        elapsed = time.time() - self.anthropic_last_call
        if elapsed < self.anthropic_interval:
            jitter = random.uniform(0, self.anthropic_interval * 0.2)
            wait_time = (self.anthropic_interval - elapsed) + jitter
            time.sleep(wait_time)
        self.anthropic_last_call = time.time()

    def ask_openai(self, prompt, model=None):
        """Ask OpenAI."""
        if model is None:
            model = Config.OPENAI_MODEL
        
        self._wait_openai()
        
        input_tokens = count_tokens(prompt, model)
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        output_text = response.choices[0].message.content
        output_tokens = count_tokens(output_text, model)
        
        # Track cost
        cost = self.cost_tracker.track_request("openai", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        
        return output_text
    
    def ask_anthropic(self, prompt, model=None):
        """Ask Anthropic."""
        if model is None:
            model = Config.ANTHROPIC_MODEL
        
        self._wait_anthropic()
        
        input_tokens = count_tokens(prompt, model)
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        output_text = response.content[0].text
        output_tokens = count_tokens(output_text, model)
        
        # Track cost
        cost = self.cost_tracker.track_request("anthropic", model, input_tokens, output_tokens)
        self.cost_tracker.check_budget(Config.DAILY_BUDGET)
        
        return output_text
    
    def ask_with_fallback(self, prompt, primary="openai"):
        """
        Ask with fallback to secondary provider.
        
        Args:
            prompt: Question to ask
            primary: Primary provider ("openai" or "anthropic")
        
        Returns:
            Dictionary with provider used and response
        """
        try:
            if primary == "openai":
                print("Trying OpenAI (primary)...")
                response = self.ask_openai(prompt)
                return {"provider": "openai", "response": response}
            else:
                print("Trying Anthropic (primary)...")
                response = self.ask_anthropic(prompt)
                return {"provider": "anthropic", "response": response}
        
        except Exception as e:
            print(f"✗ Primary provider failed: {e}")
            print("Falling back to secondary provider...")
            
            try:
                if primary == "openai":
                    response = self.ask_anthropic(prompt)
                    return {"provider": "anthropic", "response": response}
                else:
                    response = self.ask_openai(prompt)
                    return {"provider": "openai", "response": response}
            
            except Exception as e2:
                print(f"✗ Secondary provider also failed: {e2}")
                raise Exception("All providers failed")

# Test the module
if __name__ == "__main__":
    providers = LLMProviders()
    
    # Test OpenAI
    print("Testing OpenAI:")
    response = providers.ask_openai("What is Python? Answer in one sentence.")
    print(f"Response: {response}\n")
    
    # Test Anthropic
    print("Testing Anthropic:")
    response = providers.ask_anthropic("What is Python? Answer in one sentence.")
    print(f"Response: {response}\n")
    
    # Test fallback
    print("Testing fallback:")
    result = providers.ask_with_fallback("What is machine learning? Answer in one sentence.")
    print(f"Provider used: {result['provider']}")
    print(f"Response: {result['response']}\n")
    
    # Show cost summary
    summary = providers.cost_tracker.get_summary()
    print(f"Total cost: ${summary['total_cost']:.4f}")
    print(f"Total requests: {summary['total_requests']}")
