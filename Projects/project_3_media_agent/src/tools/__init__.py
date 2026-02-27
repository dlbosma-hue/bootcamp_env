# Tools package for Media Diversity Watch agent
# MCP-compatible tools using LangChain @tool decorator
#
# Tool 1: rag_query_tool    — searches the Pinecone knowledge base for benchmarks
# Tool 2: search_wikipedia  — fetches company background from Wikipedia
# Tool 3: search_newsapi    — searches recent news about diversity practices
# Tool 4: analyse_rss_feed  — primary source: bylines, keywords, language flags

from .rss_tool import analyse_rss_feed
from .wikipedia_tool import search_wikipedia
from .newsapi_tool import search_newsapi
from .rag_tool import rag_query_tool

__all__ = ["analyse_rss_feed", "search_wikipedia", "search_newsapi", "rag_query_tool"]
