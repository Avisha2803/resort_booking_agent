#!/usr/bin/env python3
"""Test Gemini API key"""

import os
from dotenv import load_dotenv

# Load .env from backend
load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")

print("🔑 Testing Gemini API Key...")
print(f"Key loaded: {'YES' if api_key else 'NO'}")
if api_key:
    print(f"Key starts with: {api_key[:10]}...")
    print(f"Key length: {len(api_key)}")
    
    # Try to configure
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # List available models
        models = genai.list_models()
        gemini_models = [m.name for m in models if 'gemini' in m.name]
        print(f"✅ Available Gemini models: {len(gemini_models)}")
        for model in gemini_models[:3]:  # Show first 3
            print(f"   - {model}")
            
    except Exception as e:
        print(f"❌ Gemini error: {e}")
else:
    print("❌ No API key found")
    print("\n💡 How to get a Gemini API key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Login with Google")
    print("3. Click 'Create API Key'")
    print("4. Copy the key")
    print("5. Add to backend/.env file as: GEMINI_API_KEY=your_key_here")