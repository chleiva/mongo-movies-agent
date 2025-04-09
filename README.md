# 🎬 MongoAgent: Semantic Movie Search with MongoDB & OpenAI Embeddings

**MongoAgent** is a fully serverless, intelligent search solution that enables natural language search over the `sample_mflix.movies` dataset. Leveraging **OpenAI’s `text-embedding-3-large`** model, **MongoDB Atlas Vector Search**, and **AWS infrastructure**, this solution supports semantic, hybrid, and intelligent retrieval across movie metadata and narratives.

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

> (multimodal has not been implemented)

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

## 📘 API Documentation

This project follows the [OpenAPI Specification (Swagger)](https://swagger.io/specification/) for defining endpoints, parameters, request/response schemas, and error handling.

👉 **To explore the full API interactively**, open the [`apidef.yaml`](./apidef.yaml) file using a Swagger UI-compatible viewer like:

- [https://editor.swagger.io/](https://editor.swagger.io/)
- VS Code with the [Swagger Viewer extension](https://marketplace.visualstudio.com/items?itemName=Arjun.swagger-viewer)
- Or embed it into a self-hosted Swagger UI

---

## 🚀 Try It Live

🔗 [https://mongoagent.com](https://mongoagent.com)


Then type any `curl` command in the terminal interface or try free text search queries.


---

## 🧪 API Examples

You can interact with the backend using standard `curl` requests or directly inside the [MongoAgent UI](https://mongoagent.com), which features a built-in terminal.

### 🧠 Authentication Notes

- 🔐 **When using external tools** (e.g., terminal or Postman):  
  All endpoints **require** a valid **Cognito `id_token`** provided in the header:
  ```bash
  -H "Authorization: Bearer YOUR_ID_TOKEN"
  ```

- ✅ **When using the built-in MongoAgent terminal** at [https://mongoagent.com](https://mongoagent.com):  
  The app **automatically adds** the `Authorization` header and the API host prefix (`https://your-api.com`).  
  Therefore, you can use simpler curl commands like:

  ```bash
  curl -X DELETE "movies/67f4599e44361b09bfa5e62a"
  ```

---

### 📦 1. Create a New Movie

```bash
curl -X POST "movies" \
-H "Content-Type: application/json" \
-d '{
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

---

### 📄 2. List Movies

```bash
curl -X GET "movies?page=1&limit=5"
```

---

### 🔍 3. Get a Movie by ID

```bash
curl -X GET "movies/67f40b1a4f5d1ae32b11c2eb"
```

---

### ✏️ 4. Update a Movie

```bash
curl -X PUT "movies/67f40b1a4f5d1ae32b11c2eb" \
-H "Content-Type: application/json" \
-d '{
  "title": "The Great Train Robbery II",
  "year": 1943,
  "directors": ["Edwin S. Porter"],
  "runtime": 11,
  "genres": ["Western", "Short"],
  "languages": ["English"],
  "countries": ["USA"],
  "plot": "A group of hackers stage a brazen train hold-up...",
  "fullplot": "Among the earliest existing films in American cinema."
}'
```

---

### 🗑️ 5. Delete a Movie

```bash
curl -X DELETE "movies/67f4599e44361b09bfa5e62a"
```

---

### 🔎 6. Semantic Search

```bash
curl -X POST "movies/search?n=5&reranking=true" \
-H "Content-Type: application/json" \
-d '{
  "request": "space adventures in the 1980s"
}'
```

---

### 🔀 7. Hybrid Search

```bash
curl -X POST "movies/search?hybrid=true&n=5&reranking=true" \
-H "Content-Type: application/json" \
-d '{
  "request": "thrillers directed by Christopher Nolan"
}'
```

---

### 🤖 8. LLM-Assisted Search (Agentic Retrieval)

```bash
curl -X POST "movies/search?agent=true" \
-H "Content-Type: application/json" \
-d '{
  "request": "animated movies with animals on the poster"
}'
```

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
