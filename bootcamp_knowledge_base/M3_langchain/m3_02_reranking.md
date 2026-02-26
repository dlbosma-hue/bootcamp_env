# LAB M3.02 - Relevance Scoring and Reranking

## Use Case
Improve retrieval quality in a RAG system for a legal tech company by adding a reranking step after the initial vector search. The system searches across two document types: a PDF (AI literacy practices) and a podcast transcript (trustworthy AI).

## The Problem with Basic Vector Search
Cosine similarity scores from Pinecone cluster tightly together (e.g. 0.84 to 0.89). This makes it hard to distinguish truly relevant results from loosely related ones. A chunk ranked 7th by cosine similarity might actually be the best answer.

## Two-Stage RAG Pipeline

### Stage 1: Vector Search (broad retrieval)
Retrieve the top 10 to 20 chunks by cosine similarity from Pinecone. This is fast but imprecise.

### Stage 2: Reranking (precision filtering)
Pass all retrieved chunks through Cohere's reranker model. It scores each chunk specifically for relevance to the query. Results are reordered. Keep only the top 3 to 5.

```python
from cohere import Client

co = Client(api_key=os.getenv("COHERE_API_KEY"))

results = co.rerank(
    query="What are the requirements for AI transparency?",
    documents=[chunk["text"] for chunk in retrieved_chunks],
    model="rerank-v3.5",
    top_n=5
)
```

## Why Reranking Works Better
- Cosine similarity measures general semantic closeness
- Rerankers are trained specifically to score query-document relevance
- Reranker scores spread meaningfully (0.44 to 0.85) vs cosine scores clustering (0.84 to 0.89)

## Results from This Lab
- Baseline retrieval (cosine only): 1 out of 4 test queries answered correctly
- With reranking: 2 out of 4 test queries answered correctly
- Notable example: a chunk ranked 7th by cosine similarity was correctly promoted to 1st by the reranker

## Simple Toggle Flag
The lab used a boolean flag to switch between baseline and reranked modes:
```python
USE_RERANKER = True  # set to False for baseline comparison
```

## Metadata Tagging for Filtering
Each chunk stored in Pinecone included metadata:
```python
metadata = {
    "source": "podcast_transcript",
    "chunk_id": "abc123",
    "content_hash": hashlib.md5(text.encode()).hexdigest()
}
```
`content_hash` prevents duplicate chunks from being stored if the ingestion pipeline runs multiple times.

## Key Learning
Reranking is a cheap but powerful upgrade. Cohere's reranker costs very little per call compared to an LLM and meaningfully improves which chunks the LLM sees. The single API call approach is also more efficient than LLM-based scoring which requires multiple calls.
