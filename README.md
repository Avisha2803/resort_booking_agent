# 🌿 Resort Booking Agent  
### AI-Powered Conversational Resort Management System

---

## 📌 Project Overview

The **Resort Booking Agent** is an **AI-powered conversational system** designed to simulate real-world resort operations.  
It allows guests to place **food orders** and **service requests** through a chat interface, while administrators manage these operations via a **real-time dashboard**.

The system is built using a **modular backend architecture**, combining **agentic AI**, **multi-turn conversations**, **REST APIs**, and a **Streamlit-based admin dashboard**.

This project demonstrates how **AI agents can be integrated into operational workflows** in the hospitality domain.

---

## 🎯 Objectives

- To design a **conversational AI agent** capable of handling multiple user intents  
- To implement **multi-turn confirmation flows** for reliable order handling  
- To build a **backend system** that connects AI decisions with real database operations  
- To provide an **admin-facing dashboard** for monitoring and updating resort operations  
- To follow **clean software engineering and Git practices**

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
│ ├── agents.py # AI agent & intent routing logic
│ ├── tools.py # Order and service handling functions
│ ├── models.py # Data models
│ └── database.py # SQLite database operations
│
├── dashboard/
│ └── app.py # Streamlit admin dashboard
│
├── frontend/
│ ├── index.html # Chat interface UI
│ ├── app.js # Frontend logic
│ └── style.css # Styling
│
├── run.py # Application runner
├── requirements.txt # Python dependencies
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
