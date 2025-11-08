# Akij Sales Intelligence Backend

Multi-Agent Sales Analytics System with RAG (Retrieval-Augmented Generation)

## Architecture

```
┌─────────────────────────────────────────┐
│          FastAPI Backend                │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Agent Orchestrator (Router)     │ │
│  └───────────────┬───────────────────┘ │
│                  │                     │
│    ┌─────────────┼──────────────┐     │
│    │             │              │     │
│    ▼             ▼              ▼     │
│  ┌───────┐   ┌──────────┐  ┌───────┐ │
│  │ Data  │   │Detective │  │Forecast│ │
│  │Analyst│   │  Agent   │  │ Agent  │ │
│  └───────┘   └──────────┘  └───────┘ │
│      │                                │
│      ▼                                │
│  ┌──────────┐                         │
│  │Strategist│                         │
│  │  Agent   │                         │
│  └──────────┘                         │
│                                       │
│  ┌───────────────────────────────────┐│
│  │ Services: RAG, Data, LLM, Executor││
│  └───────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## 4 Specialized Agents

1. **Data Analyst Agent** (Descriptive Analytics)
   - Answers: "What happened?"
   - Examples: "Total sales in 2024?", "Top 10 products?"

2. **Detective Agent** (Diagnostic Analytics)
   - Answers: "Why did it happen?"
   - Examples: "Why did sales drop in Q2 2023?"

3. **Forecaster Agent** (Predictive Analytics)
   - Answers: "What will happen?"
   - Examples: "Forecast next quarter sales"

4. **Strategist Agent** (Prescriptive Analytics)
   - Answers: "What should we do?"
   - Examples: "Should we open a new branch?"

## Folder Structure

```
backend/
├── main.py                  # FastAPI application entry point
├── config/                  # Configuration and settings
│   └── settings.py
├── services/                # Core services
│   ├── rag_service.py       # FAISS vector retrieval
│   ├── data_service.py      # Sales data management
│   ├── llm_service.py       # Gemini/OpenAI interface
│   └── code_executor.py     # Safe Pandas execution
├── agents/                  # 4 specialized agents
│   ├── base_agent.py
│   ├── data_analyst_agent.py
│   ├── detective_agent.py
│   ├── forecaster_agent.py
│   └── strategist_agent.py
├── orchestrator/            # Query routing
│   └── router.py
├── api/                     # API routes
│   └── routes.py
├── models/                  # Pydantic models
│   ├── request.py
│   └── response.py
└── static/                  # Frontend files (HTML/CSS/JS)
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (`.env` file):
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Create FAISS index** (if not done):
   ```bash
   python data_generation_code/create_faiss_knowledge_base.py
   ```

## Running the Server

### Option 1: Direct Python
```bash
python -m backend.main
```

### Option 2: Uvicorn
```bash
uvicorn backend.main:app --reload --port 8000
```

### Option 3: From backend directory
```bash
cd backend
python main.py
```

Server will start at: **http://localhost:8000**

## API Endpoints

### 1. Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What was total sales in 2024?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Total sales in 2024 were ৳1.17 billion...",
  "data": {...},
  "visualizations": [{
    "type": "bar",
    "data": {...}
  }],
  "agent": "Data Analyst Agent",
  "query_type": "Descriptive Analytics"
}
```

### 2. Health Check
```http
GET /api/health
```

### 3. Test Endpoint
```http
GET /api/test
```

### 4. API Documentation
Visit: **http://localhost:8000/docs**

## Testing with cURL

```bash
# Test endpoint
curl http://localhost:8000/api/test

# Health check
curl http://localhost:8000/api/health

# Chat query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What was total sales in 2024?"}'
```

## How It Works

1. **User sends query** → POST /api/chat
2. **Orchestrator routes** query to appropriate agent based on keywords
3. **Agent retrieves context** from FAISS RAG
4. **Agent generates** Pandas code using Gemini
5. **Code executor** runs code safely on sales data
6. **Agent formats** response with natural language + visualizations
7. **API returns** JSON with answer, data, and chart specifications

## Agent Routing Logic

- **Prescriptive** (should, recommend, optimize, strategy)
- **Predictive** (will, forecast, predict, future)
- **Diagnostic** (why, reason, cause, explain)
- **Descriptive** (default - what, total, show, list)

## Tech Stack

- **Framework:** FastAPI
- **LLM:** Google Gemini (via langchain-google-genai)
- **RAG:** FAISS + HuggingFace Embeddings
- **Data:** Pandas + NumPy
- **Validation:** Pydantic

## Example Queries

- "What is the total revenue for 2024?"
- "Which products are the top sellers?"
- "Why did FMCG sales drop in Q2 2023?"
- "Forecast cement sales for next quarter"
- "Should we open a new branch in Khulna?"

## Notes

- Agents initialize **lazily** (on first API request) to improve startup time
- All agents share the same RAG, Data, and LLM services
- Code execution is sandboxed for security
- Gemini API key must be set in `.env` file

## Troubleshooting

**Error: FAISS index not found**
```bash
python data_generation_code/create_faiss_knowledge_base.py
```

**Error: GEMINI_API_KEY not set**
Create `.env` file with:
```
GEMINI_API_KEY=your_key_here
```

**Error: Module not found**
```bash
pip install -r requirements.txt
```
