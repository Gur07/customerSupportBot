# 🧠 Customer Support Copilot  
### An AI-powered assistant for automating customer ticket classification and intelligent response generation

---

## 🌍 Overview  

Customer support teams handle hundreds of tickets every day — from simple “how-to” queries to complex technical issues. As organizations scale, **manually triaging and responding to tickets becomes inefficient and inconsistent**.  

The **Customer Support Copilot** is designed to solve this challenge by providing an **AI-driven helpdesk assistant** that can:
- Automatically **classify incoming tickets** by topic, sentiment, and priority  
- **Generate context-aware responses** using Retrieval-Augmented Generation (RAG)  
- Provide an **interactive demo interface** to visualize the AI pipeline’s reasoning and final responses  

This project demonstrates the **core AI pipeline** for a customer support automation system — complete with classification, retrieval, and intelligent response generation.

---

## 🎯 Objectives  

The project has two main goals:

### 1. **Bulk Ticket Classification Dashboard**
- Load and display all support tickets from a sample dataset  
- Automatically classify each ticket based on:
  - **Topic Tags:** e.g., How-to, Product, API/SDK, SSO, Best Practices, Sensitive Data, etc.  
  - **Sentiment:** e.g., Frustrated, Curious, Angry, Neutral  
  - **Priority:** P0 (High), P1 (Medium), P2 (Low)  
- Display these attributes in a clean dashboard view  

### 2. **Interactive AI Agent**
- Allow users to **submit new support queries**
- Display:
  - **Internal Analysis View** — AI’s reasoning: topic, sentiment, and priority  
  - **Final Response View** — the system’s answer or routing message  

- If the topic belongs to *How-to*, *Product*, *API/SDK*, *Best Practices*, or *SSO*:  
  → Use a **RAG pipeline** to fetch relevant answers from documentation sources and cite URLs.  
- Otherwise:  
  → Display a routing message like “This ticket has been classified as a ‘Connector’ issue and routed to the appropriate team.”

---

## ⚙️ System Architecture  

Below is a high-level flow of how the system operates:

                    ┌────────────────────┐
                    │ Sample Tickets CSV │
                    └─────────┬──────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Classification  │
                     │  Pipeline       │
                     ├─────────────────┤
                     │ Topic Tagging   │
                     │ Sentiment       │
                     │ Priority Scoring│
                     └─────────┬────────┘
                               │
        ┌──────────────────────┼────────────────────────┐
        ▼                      ▼                        ▼
 ┌──────────────┐      ┌────────────────┐       ┌─────────────────┐
 │ Bulk Ticket  │      │ Interactive AI │       │ RAG Knowledge   │
 │ Dashboard    │      │  Chat Input    │       │  Retrieval      │
 └──────┬───────┘      └──────┬────────┘       └─────────────────┘
        │                     │
        ▼                     ▼
  ┌──────────────────────────────────────┐
  │    Front-End Views                   │
  │  • Internal Analysis (Topic, etc.)   │
  │  • Final Response (Generated Text)   │
  └──────────────────────────────────────┘


---

## 🧩 AI Pipeline Design  

### 1. **Ticket Classification**
**Goal:** Identify the *topic*, *sentiment*, and *priority* for each incoming ticket.  

#### Steps:
- **Embedding-based classification:**  
  Use sentence embeddings (e.g., `all-MiniLM-L6-v2`) for semantic understanding.  
- **Fine-tuned zero-shot model or LLM prompt-based classification** for:
  - **Topic detection**
  - **Sentiment classification**
  - **Priority estimation** based on urgency words or tone  

---

### 2. **RAG (Retrieval-Augmented Generation) Pipeline**

**Goal:** Generate accurate, citation-backed answers for tickets related to Product, API/SDK, SSO, or Best Practices.

#### Steps:
1. **Fetch context documents** from internal knowledge sources (e.g., docs, developer hub).  
2. **Split and embed documents** using vector embeddings (FAISS / Chroma).  
3. **Retrieve top-k relevant chunks** based on user query similarity.  
4. **Generate final answer** using an LLM (e.g., Gemini, GPT, or local model) combined with retrieved context.  
5. **Cite sources (URLs)** used in the answer.  

---

### 3. **Response Routing**
If the ticket is outside supported topics (e.g., Connector, Lineage, Sensitive Data), the system automatically responds with:
> “This ticket has been classified as a ‘Connector’ issue and routed to the appropriate team.”

---

## 🖥️ Application Interface  

The application can be built using:
- **Streamlit** (recommended for simplicity and interactivity)
- Or **Flask + React** (for scalability and UI flexibility)

### Components:
- **Sidebar:** Upload or view ticket dataset  
- **Dashboard View:** Show classified tickets with color-coded sentiment/priority tags  
- **Chat Interface:** Input new queries and view AI’s reasoning + response  

---

## 🧠 Model & Tooling Choices  

| Task | Suggested Tool / Model | Reason |
|------|------------------------|--------|
| Topic, Sentiment, Priority Classification | OpenAI / Gemini / HuggingFace zero-shot models | Fast prototyping, no custom training |
| Text Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Lightweight & high accuracy |
| Vector Database | FAISS or Chroma | Efficient similarity search for RAG |
| LLM for RAG | Gemini API / GPT / Llama 3 | Contextual and citation-friendly |
| Frontend Framework | Streamlit | Quick deployment and demo |
| Backend | Python (FastAPI / Flask) | API flexibility and modular design |

---

## 🧱 Folder Structure  

customer-support-copilot/
│
├── app.py                 # Main Streamlit or Flask app
├── backend/
│   ├── classifier.py      # Topic, sentiment, priority classification logic
│   ├── rag_engine.py      # RAG pipeline implementation
│   ├── utils.py           # Helper functions
│
├── data/
│   └── sample_tickets.csv # Sample ticket dataset
│
├── docs/
│   ├── architecture.png   # System diagram
│
├── requirements.txt       # Dependencies
├── README.md              # Documentation
└── config.yaml            # Model/API configurations
