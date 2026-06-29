<div align="center">

# 🌱 ESG Risk Intelligence Hub
### Multi-Agent Sustainability Disclosures & Controversy Analysis System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C?style=for-the-badge&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Llama](https://img.shields.io/badge/Llama_3.1-Groq_LPU-0467DF?style=for-the-badge&logoColor=white)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B35?style=for-the-badge&logoColor=white)](https://chromadb.com)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML_Classifier-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

**Enter any company name. Get a full ESG Risk Intelligence Report in seconds — powered by 4 autonomous AI agents.**

</div>

---

## 🎯 What Is This?

The **ESG Risk Intelligence Hub** is a production-grade, multi-agent AI system that automatically generates structured ESG (Environmental, Social, Governance) risk reports for any publicly known company.

Traditional ESG risk assessment requires analysts to spend **days** manually reading news, sustainability reports, and regulatory filings. This system automates the entire workflow using a **LangGraph-orchestrated pipeline of 4 specialized AI agents** — delivering a comprehensive risk report in under 60 seconds.

> *Enter "Tesla" → Get a structured ESG report with E/S/G risk scores, controversy analysis, benchmark comparisons, and actionable insights — instantly.*

---

## 🏗️ Architecture — 4-Agent Pipeline

```
User Input: Company Name
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              LangGraph State Machine                │
│                                                     │
│  ┌─────────────┐    ┌──────────────┐               │
│  │  Agent 1    │───▶│   Agent 2    │               │
│  │  Scraper    │    │  Classifier  │               │
│  │ DuckDuckGo  │    │ Scikit-Learn │               │
│  │ News Search │    │ E/S/G Risks  │               │
│  └─────────────┘    └──────┬───────┘               │
│                            │                        │
│  ┌─────────────┐    ┌──────▼───────┐               │
│  │  Agent 4    │◀───│   Agent 3    │               │
│  │  Synthesis  │    │  RAG Agent   │               │
│  │  Llama 3.1  │    │  ChromaDB    │               │
│  │  via Groq   │    │  Benchmarks  │               │
│  └──────┬──────┘    └─────────────┘               │
│         │                                           │
└─────────┼───────────────────────────────────────────┘
          │
          ▼
  Structured ESG Risk Report
  (E/S/G scores + analysis + citations)
```

### Agent Breakdown

| Agent | Role | Technology |
|---|---|---|
| 🕵️ **Scraper Agent** | Fetches recent ESG news, controversies & sustainability disclosures for the company | DuckDuckGo Search + LangChain |
| 🧠 **Classifier Agent** | Classifies each piece of content as Low / Medium / High risk across Environmental, Social, and Governance dimensions separately | Scikit-learn ML Model |
| 📚 **RAG Agent** | Retrieves relevant ESG benchmark standards and industry comparisons from vector store | ChromaDB + Sentence-Transformers |
| ✍️ **Synthesis Agent** | Combines all signals into a structured, cited ESG Intelligence Report | Llama 3.1 via Groq LPU |

---

## ✨ Key Features

- **🔄 Fully Automated Pipeline** — One company name input triggers the entire 4-agent workflow automatically
- **📊 Separate E/S/G Scoring** — Environmental, Social, and Governance risks scored independently (Low / Medium / High)
- **⚡ Ultra-Low Latency** — Groq's LPU delivers Llama 3.1 responses in milliseconds
- **📚 RAG-Grounded Analysis** — Reports are grounded in real ESG benchmark data, not hallucinated content
- **🎨 Premium Dark UI** — Glassmorphism-styled Streamlit dashboard with real-time agent status tracking
- **🔐 Fallback Mode** — Works without a Groq API key using a comprehensive template fallback

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Agent Orchestration | LangGraph (StateGraph) |
| LLM | Llama 3.1 via Groq API |
| RAG Framework | LangChain + ChromaDB |
| Embeddings | Sentence-Transformers |
| ML Classifier | Scikit-learn |
| Web Scraping | DuckDuckGo Search |
| Frontend | Streamlit |
| Environment | python-dotenv |

---

## 🚀 Getting Started

### Prerequisites
```
Python 3.11+
Groq API key — free at console.groq.com
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Jidnyesha-403/ESG-Risk-Intelligence-Agent.git
cd ESG-Risk-Intelligence-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Add your GROQ_API_KEY to the .env file

# 4. Train the ESG classifier & seed ChromaDB
# (Click "Train ESG Model & Seed DB" in the sidebar after launching, OR run manually)

# 5. Launch the app
streamlit run app.py
```

### Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: **https://console.groq.com**

---

## 📁 Project Structure

```
ESG-Risk-Intelligence-Agent/
├── app.py                          # Main Streamlit application & UI
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore
├── test_pipeline.py                # Pipeline testing script
├── test_report.md                  # Sample generated report
├── chroma_db/                      # ChromaDB persistent vector store
└── src/
    ├── agents/
    │   ├── graph.py                # LangGraph StateGraph orchestration
    │   ├── collector.py            # Agent 1: Web scraper
    │   ├── classifier.py           # Agent 2: ML risk classifier
    │   ├── retriever.py            # Agent 3: RAG retriever
    │   └── generator.py            # Agent 4: Report synthesizer
    └── utils/
        ├── model_trainer.py        # Trains & saves Scikit-learn ESG model
        └── db_initializer.py       # Seeds ChromaDB with ESG benchmarks
```

---

## 💡 How to Use

1. **Launch the app** with `streamlit run app.py`
2. **Add your Groq API key** in the sidebar under System Settings
3. **First time only:** Click **"Train ESG Model & Seed DB"** in the sidebar — this trains the ML classifier and populates ChromaDB with ESG benchmark data
4. **Enter a company name** (e.g., Tesla, Apple, ExxonMobil, Amazon)
5. **Click "Generate ESG Risk Analysis"** and watch all 4 agents work in real-time
6. **View your report** — E/S/G risk cards + full structured intelligence report

---

## 📊 Sample Output

For a company like **Tesla**, the system outputs:

```
Environmental Risk:  MEDIUM
Social Risk:         HIGH  
Governance Risk:     LOW

Full Report:
- Executive Summary
- Key ESG Controversies Identified
- Environmental Risk Analysis (with citations)
- Social Risk Analysis (with citations)
- Governance Risk Analysis (with citations)
- Industry Benchmark Comparison
- Actionable Recommendations
```

---

## 🔍 Why RAG + ML + Agents?

**Pure LLM approach:** Hallucinated company facts, outdated information, no citations

**This system's approach:**
- Agent 1 fetches **real, current** news about the specific company
- Agent 2 uses a **trained ML model** for consistent, objective risk classification
- Agent 3 retrieves **actual ESG benchmark standards** for comparison
- Agent 4 synthesizes only **grounded, cited** insights

Result: Zero hallucinations on company-specific facts.

---

## 🙋 About the Developer

Built by **Jidnyesha Ahirrao** — AI & GenAI Engineering, Data Science, Python Development.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/jidnyesha-ahirrao-061401255/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/Jidnyesha-403)
[![AuraStyle AI](https://img.shields.io/badge/Also_see-AuraStyle_AI-FF6B6B?style=flat-square)](https://epicfashionzone.in)

---

<div align="center">

⭐ **Star this repo if you found it useful!**

*Built with LangGraph · ChromaDB · Llama 3.1 · Scikit-learn · Streamlit*

<<<<<<< HEAD
</div>
=======
</div>
>>>>>>> 52232051e531cc68e383727b24bba4b0098b28e7
