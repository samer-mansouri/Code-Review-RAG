import json
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain.schema import Generation
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.openrouter_config import OpenRouterLLM
from dotenv import load_dotenv

load_dotenv()

# Prompt Template
prompt_template = PromptTemplate.from_template("""
You are a senior software engineer reviewing the following Git patch.

Your task is to return a **valid JSON object only** — strictly following this exact format:

{{
  "file": "<filename>",
  "issues": [
    {{
      "severity": "<critical|warning|suggestion|minor>",
      "type": "<short category name>",
      "message": "<short description of the issue>",
      "line_reference": "<line number(s)>",
      "suggested_fix": "<concise fix suggestion>"
    }}
  ],
  "summary": {{
    "critical": <int>,
    "warning": <int>,
    "suggestion": <int>
  }}
}}

Do not add explanations, markdown, comments, or prose. Only output raw JSON.

### Git Patch:
{patch}

### Relevant Past Reviews:
{related_reviews}
""")

# Embedding and Retriever Setup
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
retriever = FAISS.load_local(
    "index/qwen_rag_index",
    embeddings=embedding,
    allow_dangerous_deserialization=True
).as_retriever()

llm = OpenRouterLLM(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="qwen/qwen-2.5-coder-32b-instruct:free"
)

# Extract keywords from patch
def extract_keywords(patch):
    return list(set(re.findall(r'\b\w+\b', patch.lower())))

# Filter retrieved documents
def filter_docs(docs, keywords):
    filtered = []
    for doc in docs:
        text = doc.page_content.lower()
        if any(kw in text for kw in keywords):
            filtered.append(doc)
    return filtered

# Main review function
def review_patch_with_rag(patch_text: str):
    docs = retriever.get_relevant_documents(patch_text)
    keywords = extract_keywords(patch_text)
    filtered_docs = filter_docs(docs, keywords)

    related = "\n\n---\n\n".join([d.page_content for d in filtered_docs[:10]])  # Limit for prompt size

    chain = (
        prompt_template |
        RunnableLambda(lambda p: Generation(text=llm.invoke(p.to_string())))
    )

    result = chain.invoke({"patch": patch_text, "related_reviews": related})
    return result.text
