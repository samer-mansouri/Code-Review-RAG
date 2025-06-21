# Git Patch Reviewer with RAG & AI

## Description

This project provides an AI-powered code review assistant for GitHub and GitLab pull/merge requests. It utilizes a Retrieval-Augmented Generation (RAG) pipeline to enhance the quality of patch analysis using historical review data. The system supports integration via REST APIs and automatically stores results in MongoDB.

## Features

* AI-based review of Git patches using a large language model.
* Retrieval of relevant past reviews with FAISS and MiniLM embeddings.
* JSON-based structured issue feedback with severity levels.
* RESTful API endpoints for integration.
* MongoDB persistence for review records.

## Tools & Technologies

* **LangChain** for orchestrating the review logic.
* **FAISS** for vector similarity search.
* **HuggingFace MiniLM** (`all-MiniLM-L6-v2`) for embeddings.
* **Qwen2.5 Coder 32B Instruct** via OpenRouter for LLM responses.
* **Flask** & **CORS** for REST API backend.
* **MongoDB** for storing requests and review results.

## Dataset

The project uses the public GitHub PR comments dataset available on Kaggle:
[GitHub Public Pull Request Comments](https://www.kaggle.com/datasets/pelmers/github-public-pull-request-comments)

## REST API Endpoints

* `POST /review`: Run AI review for a GitHub or GitLab PR by ID.
* `GET /reviews`: Fetch previously generated review by PR ID and source.

## Environment Variables

Add your OpenRouter API key to a `.env` file:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Getting Started

* Install dependencies: `pip install -r requirements.txt`
* Build the index: `python scripts/build_index.py`
* Run the server: `python scripts/server.py`

---