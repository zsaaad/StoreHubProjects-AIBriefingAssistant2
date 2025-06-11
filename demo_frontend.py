#!/usr/bin/env python3
"""
Frontend Demo Script - AI Pre-Call Briefing Assistant

Quick demo script to showcase the new web interface capabilities.
"""

import time
import webbrowser
import subprocess
import requests
from datetime import datetime

def check_server_status():
    """Check if the server is running."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def open_frontend():
    """Open the frontend in the default browser."""
    try:
        webbrowser.open("http://localhost:8000/app")
        print("✅ Frontend opened in browser: http://localhost:8000/app")
        return True
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        return False

def main():
    """Run the frontend demonstration."""
    print("🎨 AI PRE-CALL BRIEFING ASSISTANT")
    print("   Frontend Demonstration")
    print("="*50)
    
    # Check if server is running
    print("🔍 Checking server status...")
    if check_server_status():
        print("✅ Backend server is running")
    else:
        print("❌ Backend server not running")
        print("💡 Start with: uvicorn main:app --reload --port 8000")
        return
    
    # Test API endpoints
    print("\n🧪 Testing API endpoints...")
    try:
        # Test generic script
        response = requests.get("http://localhost:8000/api/generic-script", timeout=5)
        if response.status_code == 200:
            print("✅ Generic script endpoint: OK")
        
        # Test mock lead
        response = requests.get("http://localhost:8000/api/mock-lead", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Mock lead endpoint: OK")
            print(f"   Sample lead: {data['contact']['name']} from {data['company']['name']}")
        
    except Exception as e:
        print(f"⚠️ API test failed: {e}")
    
    # Open frontend
    print("\n🚀 Opening frontend interface...")
    if open_frontend():
        print("\n📋 DEMONSTRATION FLOW:")
        print("1. 🔴 Generic Script Section - Shows standard approach")
        print("2. 🔵 Lead Intelligence Section - Shows available data")
        print("3. 🎯 Click 'Generate AI-Enhanced Script' button")
        print("4. ⏳ Watch AI processing animation")
        print("5. 🤖 AI-Enhanced Script Section - Shows transformation")
        print("6. 📊 View metrics and enhancement badges")
        
        print("\n🎯 KEY DEMONSTRATION POINTS:")
        print("• Transformation from 15% to 65% close rates")
        print("• Professional, personalized script generation")
        print("• Real-time AI processing with company data")
        print("• Enterprise-grade user interface")
        
        print("\n💡 STAKEHOLDER TALKING POINTS:")
        print("• 'This is how everyone else does sales calls...'")
        print("• 'Here's the intelligence we have available...'")
        print("• 'Watch the AI transformation happen live...'")
        print("• 'This is the 4X improvement in action...'")
        
        print(f"\n🌐 Frontend URL: http://localhost:8000/app")
        print("📖 Documentation: FRONTEND_README.md")
        
    else:
        print("❌ Failed to open frontend automatically")
        print("💡 Manually visit: http://localhost:8000/app")

if __name__ == "__main__":
    main() 