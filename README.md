# 🌿 Resort Booking Agent – AI-Powered Management System

An **AI-powered resort booking and management system** that enables guests to place orders and service requests through a conversational interface, while administrators manage operations via a real-time dashboard.

This project demonstrates **agentic AI**, **multi-turn conversations**, **backend APIs**, and a **Streamlit-based admin dashboard**, following an industry-style modular architecture.

---

## 🚀 Features

### 👤 Guest Side (Chat Interface)
- 💬 Conversational AI booking agent
- 🔁 Multi-turn order confirmation
- 🍽️ Food ordering
- 🛎️ Service requests (room service, housekeeping, etc.)
- 🧠 Intent-based routing (order / query / help)
- 📋 Structured responses with confirmations

### 🛠️ Admin Side (Dashboard)
- 📊 Real-time Streamlit admin dashboard
- 📦 View and manage guest orders
- 🛎️ Track service requests
- 🔄 Update order/request status
- 🗄️ SQLite-backed data persistence

---

## 🧠 System Architecture

User (Chat UI)
│
▼
Frontend (HTML / CSS / JavaScript)
│
▼
FastAPI Backend
│
├── AI Agent (Intent Router + Tools)
├── Order & Service APIs
├── SQLite Database
│
▼
Streamlit Admin Dashboard


---

## 🛠️ Tech Stack

| Layer | Technology |
|-----|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| AI / Agent | LLM-based intent routing, tool calling |
| Dashboard | Streamlit |
| Database | SQLite |
| Version Control | Git, GitHub |

---

## 📂 Project Structure

resort_booking_agent/
│
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── agents.py # AI agent & intent logic
│ ├── tools.py # Order & service tools
│ ├── models.py # Data models
│ └── database.py # SQLite operations
│
├── dashboard/
│ └── app.py # Streamlit admin dashboard
│
├── frontend/
│ ├── index.html # Chat UI
│ ├── app.js # Frontend logic
│ └── style.css # Styling
│
├── run.py # Application runner
├── requirements.txt
└── README.md


---

⚙️ How to Run Locally

1️⃣ Clone the Repository
```bash
git clone https://github.com/Avisha2803/resort_booking_agent.git
cd resort_booking_agent

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Start Backend Server
python run.py

4️⃣ Start Admin Dashboard
streamlit run dashboard/app.py

5️⃣ Open in Browser

💬 Chat Interface:
http://localhost:8080

📊 Admin Dashboard:
http://localhost:8501
