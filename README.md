# 🏠 HomePilot AI — Autonomous Property Discovery Agent

> An intelligent conversational AI agent that helps home buyers find, analyze, and rank properties through natural language interaction.

---

## 🎯 Overview

HomePilot AI is a **production-ready** autonomous property discovery agent built with **LangGraph**, **FastAPI**, and **React**. It accepts buyer preferences in natural language, autonomously decides which tools to use, gathers information from multiple data sources, ranks properties with a weighted scoring algorithm, and explains every recommendation with full transparency.

### Key Features

- **🤖 Autonomous Agent** — LangGraph-powered planner dynamically selects which tools to invoke per query
- **🗣️ Natural Language** — Express preferences in plain English: *"3BHK in Mumbai under 1.5 crore near metro"*
- **📊 Smart Ranking** — Weighted scoring across budget, commute, schools, safety, and amenities
- **💡 Explainable AI** — Every recommendation includes pros, cons, score breakdown, and reasoning
- **🧠 Conversation Memory** — Multi-turn context via LangGraph checkpointer + ChromaDB semantic search
- **🔧 6 Specialized Tools** — Property search, Google Maps, school ratings, crime analysis, price history, neighborhood data
- **🌙 Dark Mode** — Beautiful glassmorphic UI with animated transitions

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)               │
│  ┌────────┐  ┌──────────┐  ┌───────────────┐  ┌──────────┐ │
│  │  Home   │  │   Chat   │  │ Property View │  │  Browse  │ │
│  └────────┘  └──────────┘  └───────────────┘  └──────────┘ │
└────────────────────────┬─────────────────────────────────────┘
                         │  REST API (axios)
┌────────────────────────┴─────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐│
│  │                    LangGraph Agent                       ││
│  │                                                          ││
│  │  START → Planner → Router → [Tools] → Ranker → Explain  ││
│  │                        │                                  ││
│  │     ┌──────────────────┼──────────────────┐              ││
│  │     ▼         ▼        ▼         ▼        ▼              ││
│  │  Property  Google    School    Crime   Neighborhood      ││
│  │  Search    Maps      Tool     Tool    Tool               ││
│  │            + Price History                                ││
│  └──────────────────────────────────────────────────────────┘│
│  ┌──────────────────┐  ┌─────────────────────┐              │
│  │  SQLite (state)   │  │  ChromaDB (vectors) │              │
│  └──────────────────┘  └─────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

### LangGraph Agent Flow

```
START → planner → should_search?
                    ├── search → should_enrich?
                    │              ├── enrich → ranking → explanation → response → memory → END
                    │              └── ranking → explanation → response → memory → END
                    ├── enrich_only → ranking → explanation → response → memory → END
                    └── respond → memory → END
```

The **planner** uses the LLM to:
1. Classify user intent (new search / refine / compare / clarify / general question)
2. Extract preferences (city, budget, bedrooms, etc.)
3. Decide which tools to invoke
4. Adjust ranking weights dynamically

---

## 🛠️ Tech Stack

| Layer      | Technology                                    |
|------------|-----------------------------------------------|
| Backend    | Python 3.12, FastAPI, Uvicorn                 |
| Agent      | LangGraph, LangChain, OpenAI GPT-4o-mini     |
| Database   | SQLite (metadata), ChromaDB (semantic memory) |
| Frontend   | React 19, Vite, React Router, Axios           |
| Styling    | Vanilla CSS (custom design system)            |
| Deployment | Docker, Docker Compose, Render, Vercel        |

---

## 📁 Project Structure

```
HomePilot AI/
├── backend/
│   ├── agents/
│   │   ├── planner.py          # LLM-based intent & tool planner
│   │   ├── property_agent.py   # LangGraph StateGraph (core)
│   │   ├── ranking_agent.py    # LLM explanation generator
│   │   └── memory.py           # Conversation memory manager
│   ├── database/
│   │   └── database.py         # SQLite + ChromaDB wrapper
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── responses.py        # API response models
│   ├── prompts/
│   │   ├── system_prompt.txt   # Agent system instructions
│   │   ├── planner_prompt.txt  # Planner chain-of-thought prompt
│   │   └── ranking_prompt.txt  # Explanation generation prompt
│   ├── services/
│   │   ├── ranking_service.py  # Weighted scoring algorithm
│   │   ├── conversation_service.py
│   │   └── property_service.py
│   ├── tools/
│   │   ├── llm.py              # OpenAI client singleton
│   │   ├── property_search.py  # 30+ mock properties
│   │   ├── google_maps.py      # Transit & commute data
│   │   ├── school_tool.py      # School ratings
│   │   ├── crime_tool.py       # Safety analysis
│   │   ├── price_history.py    # Price trend data
│   │   └── neighborhood.py     # Amenities & walkability
│   ├── tests/
│   │   ├── test_tools.py       # Tool unit tests
│   │   ├── test_ranking.py     # Ranking algorithm tests
│   │   ├── test_api.py         # API endpoint tests
│   │   └── test_helpers.py     # Utility tests
│   ├── utils/
│   │   ├── logger.py           # Structured JSON logging
│   │   └── helpers.py          # INR formatting, parsing, etc.
│   ├── app.py                  # FastAPI application
│   ├── config.py               # Pydantic settings
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ChatBubble.jsx
│   │   │   ├── PropertyCard.jsx
│   │   │   ├── ScoreBreakdown.jsx
│   │   │   └── TypingIndicator.jsx
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   └── useDarkMode.js
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Chat.jsx
│   │   │   ├── PropertyDetails.jsx
│   │   │   └── History.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **OpenAI API key**

### 1. Clone & Configure

```bash
git clone <repository-url>
cd "HomePilot AI"

# Backend
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python app.py
```

The API will be available at **http://localhost:8000**. Docs at **http://localhost:8000/docs**.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Docker (Alternative)

```bash
# Set your API key in the environment
export OPENAI_API_KEY=sk-your-key-here

docker-compose up --build
```

Frontend at **http://localhost:3000**, Backend at **http://localhost:8000**.

---

## 📡 API Endpoints

| Method | Endpoint                 | Description                          |
|--------|--------------------------|--------------------------------------|
| GET    | `/api/health`            | Health check                         |
| POST   | `/api/chat`              | Main conversational agent endpoint   |
| POST   | `/api/search`            | Direct property search with filters  |
| GET    | `/api/property/{id}`     | Property details                     |
| GET    | `/api/history/{id}`      | Price history                        |
| POST   | `/api/rank`              | Re-rank with custom weights          |
| GET    | `/api/properties`        | Browse all properties                |
| GET    | `/api/conversation`      | Retrieve conversation history        |

### Example: Chat Request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find me a 3BHK in Bangalore under 1 crore with good schools"}'
```

---

## 🧪 Testing

```bash
cd backend
pip install pytest httpx

# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_tools.py -v
python -m pytest tests/test_ranking.py -v
python -m pytest tests/test_helpers.py -v
python -m pytest tests/test_api.py -v
```

---

## 🔧 Configuration

Environment variables (set in `.env`):

| Variable           | Default         | Description                     |
|--------------------|-----------------|---------------------------------|
| `OPENAI_API_KEY`   | *(required)*    | OpenAI API key                  |
| `OPENAI_MODEL`     | `gpt-4o-mini`   | Model for LLM calls             |
| `APP_ENV`          | `development`   | Environment (dev/production)     |
| `DEBUG`            | `true`          | Enable debug mode               |
| `HOST`             | `0.0.0.0`       | Server host                     |
| `PORT`             | `8000`          | Server port                     |
| `CORS_ORIGINS`     | `*`             | Allowed CORS origins            |
| `DATABASE_URL`     | SQLite default  | Database connection string       |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | ChromaDB persistence directory |

---

## 🧠 Agentic Behavior

This is **not** a fixed pipeline. The planner dynamically decides:

1. **Tool Selection** — Only queries tools relevant to the user's question
2. **Weight Adjustment** — "I need safety" → safety weight increases to 35%+
3. **Intent Detection** — Classifies: new search, refinement, comparison, follow-up, or general question
4. **Conditional Routing** — LangGraph edges route to only needed nodes

Example conversation flow:

```
User: "Find me a 3BHK in Mumbai under 1.5 crore"
→ Planner: intent=new_search, tools=[property_search, google_maps, school_tool, crime_tool]
→ Enriches with commute, schools, safety data
→ Ranks 10+ properties with weighted scoring
→ Explains top 5 with pros/cons

User: "Focus on the safest areas"
→ Planner: intent=refine_search, tools=[crime_tool]
→ Adjusts safety weight from 15% → 35%
→ Re-ranks with new weights
→ Explains safety-focused recommendations
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
#   H o m e P i l o t  
 #   H o m e P i l o t  
 #   H o m e P i l o t  
 