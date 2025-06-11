#!/usr/bin/env python3
"""
Presentation Launcher - AI Pre-Call Briefing Assistant

Easy-to-use launcher for stakeholder presentations with multiple demo options.
"""

import sys
import time
import requests
from stakeholder_demo import StakeholderDemo

def check_system_status():
    """Check if the AI system is running."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main presentation launcher."""
    print("🎭 AI PRE-CALL BRIEFING ASSISTANT")
    print("   Stakeholder Presentation Launcher")
    print("="*50)
    
    # Check system status
    print("🔍 Checking system status...")
    if check_system_status():
        print("✅ AI system is running and ready")
        live_demo_available = True
    else:
        print("⚠️  AI system not detected - will use recorded demo data")
        print("   To enable live demos, run: uvicorn main:app --reload --port 8000")
        live_demo_available = False
    
    print("\n📋 PRESENTATION OPTIONS:")
    print()
    print("1. 🎯 FULL STAKEHOLDER PRESENTATION (45 minutes)")
    print("   Complete 8-slide presentation with live demonstrations")
    print("   Includes: Problem, Solution, ROI, Implementation")
    print()
    print("2. ⚡ QUICK DEMO (15 minutes)")
    print("   Live AI briefing demonstration only")
    print("   Focus: Technical capability and transformation")
    print()
    print("3. 📊 ROI PRESENTATION (20 minutes)")
    print("   Business impact and financial analysis focus")
    print("   For: CFO, CEO, business stakeholders")
    print()
    print("4. 🔧 TECHNICAL DEEP-DIVE (30 minutes)")
    print("   Architecture, implementation, integration details")
    print("   For: CTO, IT, technical stakeholders")
    print()
    
    while True:
        try:
            choice = input("\nSelect presentation option (1-4): ").strip()
            
            if choice == "1":
                print("\n🎯 LAUNCHING FULL STAKEHOLDER PRESENTATION...")
                time.sleep(1)
                demo = StakeholderDemo()
                demo.run_presentation()
                break
                
            elif choice == "2":
                print("\n⚡ LAUNCHING QUICK AI DEMO...")
                time.sleep(1)
                demo = StakeholderDemo()
                demo.slide_header("QUICK AI TRANSFORMATION DEMO")
                demo.slide_4_live_demo()
                print("\n🏆 DEMO COMPLETE - Ready for questions!")
                break
                
            elif choice == "3":
                print("\n📊 LAUNCHING ROI PRESENTATION...")
                time.sleep(1)
                demo = StakeholderDemo()
                demo.slide_header("BUSINESS IMPACT PRESENTATION")
                demo.slide_3_market_impact()
                demo.slide_5_business_impact()
                demo.slide_7_investment_and_next_steps()
                print("\n💰 ROI PRESENTATION COMPLETE - Ready for financial discussion!")
                break
                
            elif choice == "4":
                print("\n🔧 LAUNCHING TECHNICAL DEEP-DIVE...")
                time.sleep(1)
                print("Technical presentation would include:")
                print("• System architecture overview")
                print("• API integration capabilities")
                print("• Security and compliance features")
                print("• Implementation timeline")
                print("• Technical requirements")
                print("\n(Full technical documentation available)")
                break
                
            else:
                print("❌ Invalid option. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Presentation cancelled. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print("\n📞 NEXT STEPS:")
    print("• Schedule follow-up meeting")
    print("• Review presentation summary")
    print("• Discuss implementation timeline")
    print("• Begin pilot program planning")

if __name__ == "__main__":
    main() 