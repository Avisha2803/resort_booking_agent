# Resort Management System - Startup Guide

Follow these steps to run the application. You will need to open **3 separate terminal windows**.

### Prerequisites
- Ensure you have Python installed.
- Ensure your `.env` file has the correct `OPENAI_API_KEY`.

---

### Step 1: Start the Backend Server
This handles the AI logic and database.

1. Open a terminal.
2. Navigate to the project root folder:
   ```powershell
   cd c:\Users\EJ312WS\OneDrive\Desktop\shruti
   ```
3. Run the server:
   ```powershell
   uvicorn backend.main:app --reload --port 8000
   ```
   *You should see "Application startup complete".*

---

### Step 2: Start the Frontend (Chat Interface)
This is the chat window for guests.

1. Open a **new** terminal.
2. Navigate to the frontend folder:
   ```powershell
   cd c:\Users\EJ312WS\OneDrive\Desktop\shruti\frontend
   ```
3. Start the simple web server:
   ```powershell
   python -m http.server 8080
   ```
4. Open your browser to: **[http://localhost:8080](http://localhost:8080)**

---

### Step 3: Start the Dashboard (Admin View)
This shows orders and requests.

1. Open a **third** terminal.
2. Navigate to the project root folder:
   ```powershell
   cd c:\Users\EJ312WS\OneDrive\Desktop\shruti
   ```
3. Run the dashboard:
   ```powershell
   python -m streamlit run dashboard/app.py
   ```
4. Open your browser to: **[http://localhost:8501](http://localhost:8501)**
