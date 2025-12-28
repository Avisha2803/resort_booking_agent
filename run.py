#!/usr/bin/env python3
"""
Eco Resort Concierge System - Startup Script
Run with: python run.py [command]
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║      🌿 ECO RESORT CONCIERGE SYSTEM      ║
    ║         Version 2.0 - Sustainable        ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "google-generativeai",
        "streamlit",
        "requests"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies found")
    return True

def setup_database():
    """Initialize database with sample data"""
    print("🗄️  Setting up database...")
    
    try:
        # Import database functions
        from backend.database import init_db
        from backend.models import MenuItem
        from backend.database import SessionLocal
        
        # Create tables
        init_db()
        
        # Check if menu items already exist
        db = SessionLocal()
        existing_items = db.query(MenuItem).count()
        db.close()
        
        if existing_items == 0:
            print("📝 Adding sample menu items...")
            # Run the menu seeder
            from add_menu_items import setup_full_database
            setup_full_database()
        else:
            print(f"✅ Database already has {existing_items} menu items")
        
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting backend server...")
    print(f"📡 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    
    # Run uvicorn in background
    backend_cmd = [
        "uvicorn", "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    return subprocess.Popen(backend_cmd)

def start_dashboard():
    """Start Streamlit dashboard"""
    print("📊 Starting dashboard...")
    print(f"🌐 Dashboard: http://localhost:8501")
    
    # Run streamlit in background
    dashboard_cmd = [
        "streamlit", "run", "dashboard/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--theme.base", "light"
    ]
    
    return subprocess.Popen(dashboard_cmd)

def open_frontend():
    """Open frontend in browser"""
    print("🌍 Opening frontend...")
    print(f"💬 Chat: file://{os.path.abspath('frontend/index.html')}")
    
    # Try to open in default browser
    try:
        import webbrowser
        frontend_path = os.path.abspath("frontend/index.html")
        webbrowser.open(f"file://{frontend_path}")
    except:
        print("⚠️  Could not open browser automatically")
        print(f"   Please open: frontend/index.html in your browser")

def health_check():
    """Check if services are running"""
    print("🏥 Performing health check...")
    
    import requests
    import time
    
    max_attempts = 10
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is healthy!")
                return True
        except:
            if i < max_attempts - 1:
                print(f"   Attempt {i+1}/{max_attempts}...")
                time.sleep(2)
    
    print("❌ Backend not responding")
    return False

def cleanup(processes):
    """Cleanup running processes"""
    print("\n🧹 Cleaning up...")
    for process in processes:
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
    print("✅ All processes stopped")

def main():
    """Main entry point"""
    print_banner()
    
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    
    if command == "start":
        # Full startup
        if not check_dependencies():
            return 1
        
        if not setup_database():
            return 1
        
        processes = []
        try:
            # Start backend
            backend_process = start_backend()
            processes.append(backend_process)
            time.sleep(3)  # Wait for backend to start
            
            # Check backend health
            if not health_check():
                cleanup(processes)
                return 1
            
            # Start dashboard
            dashboard_process = start_dashboard()
            processes.append(dashboard_process)
            time.sleep(2)
            
            # Open frontend
            open_frontend()
            
            print("\n" + "="*50)
            print("✅ SYSTEM IS RUNNING!")
            print("="*50)
            print("\n📱 Access Points:")
            print("   Chat Interface: frontend/index.html")
            print("   Dashboard: http://localhost:8501")
            print("   API Docs: http://localhost:8000/docs")
            print("\n🛑 Press Ctrl+C to stop all services")
            print("="*50)
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
        
        finally:
            cleanup(processes)
    
    elif command == "backend":
        # Start only backend
        start_backend().wait()
    
    elif command == "dashboard":
        # Start only dashboard
        start_dashboard().wait()
    
    elif command == "setup-db":
        # Setup database only
        setup_database()
    
    elif command == "seed-menu":
        # Seed menu data
        from add_menu_items import setup_full_database
        setup_full_database()
    
    elif command == "health":
        # Health check
        health_check()
    
    elif command == "help":
        print("\n📖 Available commands:")
        print("  start       - Start all services (backend + dashboard)")
        print("  backend     - Start only backend API")
        print("  dashboard   - Start only Streamlit dashboard")
        print("  setup-db    - Initialize database tables")
        print("  seed-menu   - Add sample menu items")
        print("  health      - Check backend health")
        print("  help        - Show this help")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: python run.py help")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())