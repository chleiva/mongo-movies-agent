# 🎬 MongoAgent: Semantic Movie Search with MongoDB & OpenAI Embeddings

**MongoAgent** is a fully serverless, intelligent search platform that enables natural language queries over the `sample_mflix.movies` dataset. Leveraging **OpenAI’s `text-embedding-3-large`** model, **MongoDB Atlas Vector Search**, and **AWS infrastructure**, this solution supports semantic, hybrid, and intelligent retrieval across movie metadata and narratives.

---

## ✨ Features

- 🔍 **Semantic Search** powered by [OpenAI Embeddings](https://platform.openai.com/docs/models/text-embedding-3-large)
- 🧠 **LLM-Assisted Search** with smart query understanding and reranking
- 🔀 **Hybrid Search** using MongoDB’s text and vector search with reciprocal rank fusion
- 🖼️ Optional support for **Multimodal Search** with visual features
- 🌐 Lightweight frontend in React with Amazon Cognito Auth
- 🧱 Fully deployable on AWS using CDK, Lambda, and API Gateway

---

## 🧠 Embedding Strategy

| Chunk Type              | Fields Included                                 | Embedding Model               | Tokens |
|------------------------|--------------------------------------------------|-------------------------------|--------|
| **Narrative**          | `title`, `plot`, `fullplot`                     | `text-embedding-3-large`      | ~1895  |
| **Contextual**         | `cast`, `directors`, `awards`, `languages`, `countries`, `type`, `year` (as NL) | `text-embedding-3-large` | ~615   |
| **Multimodal**         | `poster` (image)*                               | *(Not implemented yet)*       | N/A    |

> ✅ All embedding chunks are well within the model’s 8192-token limit.

---

## 🔎 Search Types

1. **Semantic Search**  
   Embed user query → search vector indexes → optionally rerank results for relevance

2. **Hybrid Search**  
   Combine vector and text indexes using [Reciprocal Rank Fusion](https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/reciprocal-rank-fusion/)

3. **Intelligent Retrieval (Agentic RAG)**  
   An LLM parses the user's query, selects optimal fields, constructs hybrid searches, reranks, and optionally augments with context or fallback messaging

---

## 🏗️ Architecture Overview

- **Frontend**: React + Vite, hosted via S3/CloudFront with Cognito login
- **Backend**: AWS Lambda, deployed via CDK
- **API Gateway**: REST endpoints protected by Cognito
- **MongoDB Atlas**: Vector indexes and text search indexes

---

## 🚀 Try It Live

🔗 [https://mongoagent.com](https://mongoagent.com)


Then type any `curl` command in the terminal interface or try free text search queries.

---

## 🧪 API Examples

**Create a Movie**
```bash
curl -X POST "movies" -H "Content-Type: application/json" -d '{
  "title": "The Great Train Robbery",
  "year": 1903,
  "directors": ["Edwin S. Porter"],
  "runtime": 11,
  "genres": ["Western", "Short"],
  "languages": ["English"],
  "countries": ["USA"],
  "plot": "A group of bandits stage a brazen train hold-up...",
  "fullplot": "Among the earliest existing films in American cinema."
}'
```

**Other commands:**
- List: `curl -X GET "movies?page=2&limit=5"`
- Get: `curl -X GET "movies/{id}"`
- Update: `curl -X PUT "movies/{id}"`
- Delete: `curl -X DELETE "movies/{id}"`

---

## 🧱 Assumptions & Notes

- Dataset is clean, English-only, no deduplication or preprocessing performed
- Designed to scale, but not yet production-optimized for:
  - High-frequency embedding generation
  - Cost monitoring
  - Sharded indexing or async pipelines

---

## 🧩 Next Steps

- Improve attribute-awareness in hybrid searches
- Add multimodal embedding support via OpenAI’s future visual models
- Enhance reranking with OpenAI-compatible rerankers (currently evaluating options)

---

## 📚 References

- [OpenAI Embeddings](https://platform.openai.com/docs/models/text-embedding-3-large)
- [MongoDB Atlas Vector Search](https://www.mongodb.com/docs/atlas/atlas-vector-search/)
- [Reciprocal Rank Fusion](https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/reciprocal-rank-fusion/)
