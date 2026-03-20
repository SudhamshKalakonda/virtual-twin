# Virtual Twin — AI-Powered Personal Chatbot

A full-stack AI platform that creates a personalized chatbot trained on your WhatsApp chat history. Upload your chats, and your digital twin learns your unique texting style, vocabulary, and personality to respond just like you.

## 📄 Research Paper
https://github.com/SudhamshKalakonda/virtual-twin/blob/main/paper/Virtual%20twin%20paper.pdf
---

##  What It Does

- Upload your WhatsApp chat export (.txt)
- AI parses and learns from YOUR messages only
- Your partner/friend chats with a bot that responds like you
- Supports multiple users with completely isolated data

---

##  Architecture
```
WhatsApp .txt Export
        ↓
   Chat Parser (regex)
        ↓
 Sentence Embeddings
        ↓
  Vector Database (ChromaDB)
        ↓
RAG Pipeline (semantic search)
        ↓
  LLM (Llama 3.3 70B via Groq)
        ↓
    Chat Response
```

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Vite |
| Backend | Python + FastAPI |
| Database | SQLite + SQLAlchemy |
| Vector DB | ChromaDB |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM | Llama 3.3 70B via Groq API |
| Auth | JWT tokens + SHA256 hashing |

---

##  How It Works (RAG Pipeline)

1. **Parse** — WhatsApp .txt is parsed, extracting only the user's messages
2. **Embed** — Each message is converted into a 384-dimensional vector using Sentence Transformers
3. **Store** — Vectors are stored in ChromaDB with a unique collection per user
4. **Retrieve** — When a new message arrives, semantic similarity search finds the 20 most relevant past responses
5. **Generate** — Llama 3.3 70B uses those examples as context to generate a reply in the user's style

---

## ✨ Features

- 🔐 Multi-user authentication with JWT
- 📁 WhatsApp chat parser (handles 65,000+ messages)
- 🧠 RAG pipeline with semantic similarity search
- 💬 Conversation memory across messages
- 🌐 Telugu + English mixed language support
- 🔒 Private — each user's data is completely isolated

---

##  Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Usage
1. Sign up with your name and WhatsApp name
2. Export your WhatsApp chat (Without Media)
3. Upload the .txt file
4. Start chatting with your twin!

---

## 📊 Results

- Parsed and processed **65,000+ real messages**
- Semantic search retrieves relevant context in **< 100ms**
- Supports **Telugu + English** mixed language conversations
- Conversation memory maintained across full session

---

##  Roadmap

- [ ] Fine-tuning Llama on personal chat data
- [ ] Cloud deployment (Railway + Vercel)
- [ ] Mobile app (React Native)
- [ ] Support for more chat platforms (Telegram, Instagram)
- [ ] Evaluation metrics for response quality

---

## 🔬 Research

This project implements and extends concepts from:
- **RAG** (Retrieval Augmented Generation) — Lewis et al., 2020
- **Sentence-BERT** — Reimers & Gurevych, 2019
- **Persona-based dialogue** — Zhang et al., 2018

*A research paper documenting the architecture, methodology and evaluation is in progress.*

---

##  Author

**Sudhamsh Kalakonda**  
[GitHub](https://github.com/SudhamshKalakonda) | [LinkedIn](#)

---

## ⚠️ Privacy Note 

This project is built with privacy in mind. Chat data never leaves your control. No messages are stored on external servers. All processing happens locally or on your own deployed instance.
