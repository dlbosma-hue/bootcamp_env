# RAG Pipeline and Dynamic Prompting

## Use Case
Build a complete Retrieval-Augmented Generation (RAG) system that answers questions about company documents by fetching relevant context from a vector database instead of relying on the LLM's general training knowledge.

## The Core Idea
Without RAG: you ask GPT a question, it answers from memory (may hallucinate or be outdated).
With RAG: you ask a question, the system first searches your documents for relevant content, then passes that content to GPT as context. GPT answers based on your documents only.

Analogy: taking an open-book exam (RAG) vs. a closed-book exam (plain LLM).

## The Full Pipeline

```
Your documents
    |
    v
Chunking (split into pieces)
    |
    v
Embedding (convert each chunk to a number vector)
    |
    v
Pinecone (store all vectors)

--- setup is done ---

User asks a question
    |
    v
Embed the question (same embedding model)
    |
    v
Pinecone similarity search (find most similar chunks)
    |
    v
Retrieved chunks passed to LLM as context
    |
    v
LLM generates grounded answer
```

## Key Code Components

### Embeddings
```python
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
```
Converts text to a list of numbers (a vector). Similar meaning = similar numbers = close together in vector space.

### Pinecone Setup
```python
from pinecone import Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("your-index-name")
```

### The Retrieval Chain
```python
from langchain.chains import RetrievalQA
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    return_source_documents=True
)
```
`k=4` means return the 4 most similar chunks.

## Dynamic Prompting
Dynamic prompting means building the prompt at runtime by inserting retrieved content into a template:

```python
prompt_template = """
Answer the question based only on the context below.
If the answer is not in the context, say you don't know.

Context: {context}
Question: {question}
Answer:
"""
```

The `{context}` slot gets filled with the retrieved chunks automatically.

## Key Learning
The prompt instruction "answer only from the context" is what prevents hallucination. Without it, the LLM will supplement retrieved content with its own training knowledge and may introduce inaccuracies. Always include a fallback instruction like "if the answer is not in the context, say so."

## Pinecone Index Notes
- Index dimension must match the embedding model dimension (text-embedding-ada-002 = 1536 dimensions)
- A dimension mismatch causes a storage failure with a cryptic error - always check this first when Pinecone fails
