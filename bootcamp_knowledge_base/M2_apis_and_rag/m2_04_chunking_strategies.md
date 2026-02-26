# LAB M2.04 - Chunking Strategies for RAG (Podcast + PDF)

## Use Case
Prepare course materials (a podcast transcript and a PDF document) for use in a RAG pipeline by splitting them into well-structured chunks that can be embedded and searched effectively.

## What is Chunking?
Before you can search a document with a vector database, you have to split it into smaller pieces (chunks). The vector database stores one embedding per chunk. When you search, it retrieves the most relevant chunks, not the whole document.

## Two Chunking Strategies Compared

### 1. Fixed-Size Chunking
Splits text at an exact character count, regardless of sentence or paragraph boundaries.
- Simple and fast
- Poor quality: cuts sentences in the middle, loses context at boundaries
- Quality score in this lab: 17 to 20% sentence boundary preservation

### 2. Recursive Character Chunking (recommended)
Tries to split at natural boundaries in order of preference:
1. Paragraph breaks (`\n\n`)
2. Line breaks (`\n`)
3. Sentence endings (`. `)
4. Word spaces (` `)

Only moves to a smaller boundary if the chunk would exceed the size limit.
- Preserves sentence and paragraph structure
- Quality score in this lab: 33 to 100% sentence boundary preservation

### Key Parameters
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,      # max characters per chunk
    chunk_overlap=50     # characters shared between consecutive chunks
)
```

`chunk_overlap` is important: it prevents context from being lost at the boundary between two chunks. The last 50 characters of chunk 1 are repeated at the start of chunk 2.

## Podcast vs PDF Chunking
- Podcasts (transcripts): longer chunks work better because the conversation flows continuously. Use 400-600 word chunks.
- PDFs (structured documents): shorter chunks with more overlap work better to capture distinct concepts per section.

## Key Learning
Chunking strategy directly affects retrieval quality. Recursive character chunking almost always outperforms fixed-size chunking for natural language documents. Always test retrieval before connecting the LLM to verify that relevant chunks are being returned.
