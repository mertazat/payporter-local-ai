# Payporter Local AI

A local LLM and RAG-based code assistant designed to analyze private source code without sending company data to external AI services.

## Project Overview

Payporter Local AI allows developers to ask natural-language questions about a source code repository.

Instead of sending the entire codebase to an external AI service, the project processes and indexes source code locally. Relevant code sections are retrieved using semantic similarity and provided as context to a locally running language model.

The main goal is to keep sensitive source code private while still benefiting from AI-assisted code analysis.

## How It Works

The system follows a simple RAG (Retrieval-Augmented Generation) pipeline:

1. Source code files are scanned.
2. Files are divided into smaller code chunks.
3. Embeddings are generated for each chunk.
4. The embeddings and code metadata are stored in a local index.
5. The user's question is converted into an embedding.
6. The most relevant code chunks are retrieved using similarity search.
7. Relevant code is sent to the local LLM as context.
8. The model generates an answer based on the retrieved source code.

## Main Components

- `scan_code.py` - Scans the source code directory.
- `chunk_code.py` - Divides source code into smaller chunks.
- `build_index.py` - Generates the local code index and embeddings.
- `search_code.py` - Searches for relevant code using semantic similarity.
- `code_assistant.py` - Main question-answering interface.
- `test_embedding.py` - Tests the embedding system.
- `test_llm.py` - Tests communication with the local language model.

## Example Questions

The assistant can answer questions such as:

- Where are payment operations implemented?
- Which functions handle user authentication?
- Where is user profile information stored?
- Which function updates a user's profile?

The system also displays the source files and relevant line ranges used to generate the answer.

## Privacy

The project is designed with privacy in mind.

Source code analysis, embeddings, retrieval, and LLM inference can be performed locally. This allows sensitive company source code to remain on the local machine instead of being sent to external AI services.

## Technologies

- Python
- Local LLM
- RAG (Retrieval-Augmented Generation)
- Embeddings
- Cosine Similarity
- Git / GitHub

## Project Status

Prototype / Proof of Concept.

Current functionality includes source code scanning, chunking, local indexing, semantic retrieval, and local LLM-based question answering.
