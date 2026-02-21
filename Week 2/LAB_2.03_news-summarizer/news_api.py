"""News API integration module."""
import requests
import time
from config import Config

class NewsAPI:
    """Fetch news articles from NewsAPI."""
    
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.last_call_time = 0
        self.min_interval = 60.0 / Config.NEWS_API_RPM  # Rate limiting
    
    def _wait_if_needed(self):
        """Wait if we need to rate limit."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"Rate limiting News API: waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
        self.last_call_time = time.time()
    
    def fetch_top_headlines(self, category="technology", country="us", max_articles=5):
        """
        Fetch top headlines.
        
        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            max_articles: Maximum number of articles to return
        
        Returns:
            List of article dictionaries
        """
        self._wait_if_needed()
        
        url = f"{self.base_url}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "category": category,
            "country": country,
            "pageSize": max_articles
        }
        
        try:
            response = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise Exception(f"News API error: {data.get('message')}")
            
            articles = data.get("articles", [])
            
            # Extract relevant fields
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", "")
                })
            
            print(f"✓ Fetched {len(processed_articles)} articles from News API")
            return processed_articles
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching news: {e}")
            return []

# Test the module
if __name__ == "__main__":
    api = NewsAPI()
    articles = api.fetch_top_headlines(category="technology", max_articles=3)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}")
