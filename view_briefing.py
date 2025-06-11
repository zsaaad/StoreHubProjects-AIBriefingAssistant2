import json

def display_briefing():
    with open('leads_db.json', 'r') as f:
        data = json.load(f)
    
    briefings_found = 0
    
    # Show all leads with briefings
    for lead in data:
        if lead.get('ai_briefing'):
            briefings_found += 1
            briefing = json.loads(lead['ai_briefing'])
            
            print(f"🤖 AI-GENERATED BRIEFING #{briefings_found} FOR {lead['name']} at {lead['company']}")
            print("="*70)
            print()
            print("📊 COMPANY PROFILE:")
            if isinstance(briefing['company_profile'], dict):
                for key, value in briefing['company_profile'].items():
                    print(f"   {key.title()}: {value}")
            else:
                print(briefing['company_profile'])
            print()
            print("📰 KEY UPDATES:")
            if isinstance(briefing['key_updates'], list):
                for update in briefing['key_updates']:
                    print(f"   • {update}")
            else:
                print(briefing['key_updates'])
            print()
            print("🎯 LEAD ANGLE:")
            print(briefing['lead_angle'])
            print()
            print("💬 CONVERSATION STARTERS:")
            for i, starter in enumerate(briefing['conversation_starters'], 1):
                print(f"{i}. {starter}")
            print()
            print("⚠️ POTENTIAL OBJECTIONS & RESPONSES:")
            for i, obj in enumerate(briefing['potential_objections'], 1):
                print(f"{i}. Objection: {obj['objection']}")
                print(f"   Response: {obj['response']}")
                print()
            print("\n" + "="*70 + "\n")
    
    if briefings_found == 0:
        print("No briefings found in database")
    else:
        print(f"📈 Total briefings generated: {briefings_found}")

if __name__ == "__main__":
    display_briefing() 