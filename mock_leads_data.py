"""
Mock Leads Database for Mei AI Agent
Contains business context and ad interaction data for personalized chat experience
"""

import csv
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MockLead:
    lead_id: str
    company_name: str
    company_domain: str
    context_id: str
    source_visual_url: str
    
    # Enhanced business intelligence from CSV
    lead_name: str = ""
    business_operation: str = ""
    merchant_current_platform: str = ""
    business_store_name: str = ""
    average_revenue_month: int = 0
    phone: str = ""
    average_orders_per_day: int = 0
    basket_size_order: int = 0
    email: str = ""
    existing_pos_system: str = ""
    industry: str = ""
    sub_industry: str = ""
    when_need_pos: str = ""
    num_outlets: int = 1
    contact_role: str = ""
    preferred_language: str = ""

# Enhanced mock leads data from CSV
MOCK_LEADS_DATA = [
    {
        "lead_id": "00Q8d000002bY1aEAF",
        "company_name": "Kopi Kulture Sdn Bhd",
        "company_domain": "facebook.com",  # Fallback for demo - original was kopikulture.my
        "context_id": "ad_001_pos",
        "source_visual_url": "https://placehold.co/1200x628/EFEFEF/333333?text=Modern+Cloud+POS",
        "lead_name": "Aiman bin Khalid",
        "business_operation": "F&B",
        "merchant_current_platform": "GrabFood",
        "business_store_name": "Kopi Kulture",
        "average_revenue_month": 35000,
        "phone": "60123456789",
        "average_orders_per_day": 80,
        "basket_size_order": 15,
        "email": "aiman.k@kopikulture.my",
        "existing_pos_system": "Manual Cash Drawer",
        "industry": "Food & Beverage",
        "sub_industry": "Cafe",
        "when_need_pos": "In 1 month",
        "num_outlets": 1,
        "contact_role": "Owner",
        "preferred_language": "English"
    },
    {
        "lead_id": "00Q8d000002bY1bEAF",
        "company_name": "The Daily Bakehouse",
        "company_domain": "stripe.com",  # Fallback for demo - original was dailybakehouse.com
        "context_id": "ad_003_loyalty", 
        "source_visual_url": "https://placehold.co/1200x628/E1F0FD/222222?text=Digital+Loyalty+App",
        "lead_name": "Cheryl Tan",
        "business_operation": "F&B",
        "merchant_current_platform": "Instagram Orders",
        "business_store_name": "The Daily Bakehouse",
        "average_revenue_month": 25000,
        "phone": "60198765432",
        "average_orders_per_day": 30,
        "basket_size_order": 28,
        "email": "cheryl.tan@dailybakehouse.com",
        "existing_pos_system": "None",
        "industry": "Food & Beverage",
        "sub_industry": "Bakery",
        "when_need_pos": "Immediately",
        "num_outlets": 1,
        "contact_role": "Founder",
        "preferred_language": "English"
    },
    {
        "lead_id": "00Q8d000002bY1cEAF",
        "company_name": "NJ Maju Enterprise",
        "company_domain": "amazon.com",  # Fallback for demo - original was nasilemakjunction.com
        "context_id": "ad_001_pos",
        "source_visual_url": "https://placehold.co/1200x628/EFEFEF/333333?text=Modern+Cloud+POS",
        "lead_name": "Ravi Chandran",
        "business_operation": "F&B",
        "merchant_current_platform": "FoodPanda",
        "business_store_name": "Nasi Lemak Junction",
        "average_revenue_month": 95000,
        "phone": "60161234567",
        "average_orders_per_day": 250,
        "basket_size_order": 13,
        "email": "ravi.c@nljunction.com",
        "existing_pos_system": "Slurp! POS",
        "industry": "Food & Beverage",
        "sub_industry": "Quick Service Restaurant",
        "when_need_pos": "In 3 months",
        "num_outlets": 3,
        "contact_role": "Operations Manager",
        "preferred_language": "Bahasa Malaysia"
    },
    {
        "lead_id": "00Q8d000002bY1dEAF", 
        "company_name": "Lila & Co Apparel",
        "company_domain": "shopify.com",  # Keep valid domain
        "context_id": "ad_002_ecommerce",
        "source_visual_url": "https://placehold.co/1200x628/FDF8E1/444444?text=Your+Online+Store",
        "lead_name": "Siti Nurhaliza",
        "business_operation": "Retail",
        "merchant_current_platform": "Shopify",
        "business_store_name": "Lila & Co Boutique",
        "average_revenue_month": 45000,
        "phone": "60112233445",
        "average_orders_per_day": 15,
        "basket_size_order": 100,
        "email": "siti@lilaandco.shop",
        "existing_pos_system": "Shopify POS",
        "industry": "Retail",
        "sub_industry": "Fashion & Apparel",
        "when_need_pos": "Researching options",
        "num_outlets": 1,
        "contact_role": "Owner",
        "preferred_language": "Bahasa Malaysia"
    },
    {
        "lead_id": "00Q8d000002bY1eEAF",
        "company_name": "Boba Bliss Holdings",
        "company_domain": "square.com",  # Fallback for demo - original was bobabliss.my
        "context_id": "ad_003_loyalty", 
        "source_visual_url": "https://placehold.co/1200x628/E1F0FD/222222?text=Digital+Loyalty+App",
        "lead_name": "Lee Wei Shen",
        "business_operation": "F&B",
        "merchant_current_platform": "BeepIt by StoreHub",
        "business_store_name": "Boba Bliss PJ",
        "average_revenue_month": 60000,
        "phone": "60189988776",
        "average_orders_per_day": 150,
        "basket_size_order": 13,
        "email": "ws.lee@bobabliss.my",
        "existing_pos_system": "StoreHub",
        "industry": "Food & Beverage",
        "sub_industry": "Beverage / Kiosk",
        "when_need_pos": "In 2 months",
        "num_outlets": 2,
        "contact_role": "Co-Founder",
        "preferred_language": "Mandarin"
    },
    {
        "lead_id": "00Q8d000002bY1fEAF",
        "company_name": "Chapter One Ventures",
        "company_domain": "wix.com",  # Fallback for demo - original was chapteronebooks.com.my
        "context_id": "ad_002_ecommerce",
        "source_visual_url": "https://placehold.co/1200x628/FDF8E1/444444?text=Your+Online+Store",
        "lead_name": "Farah Adibah",
        "business_operation": "Retail",
        "merchant_current_platform": "Website (Wix)",
        "business_store_name": "Chapter One Books",
        "average_revenue_month": 30000,
        "phone": "60176543210",
        "average_orders_per_day": 10,
        "basket_size_order": 100,
        "email": "farah.a@chapteronebooks.com.my",
        "existing_pos_system": "Manual Cash Drawer",
        "industry": "Retail",
        "sub_industry": "Books & Stationery",
        "when_need_pos": "Immediately",
        "num_outlets": 1,
        "contact_role": "Manager",
        "preferred_language": "English"
    },
    {
        "lead_id": "00Q8d000002bY1gEAF",
        "company_name": "Zenith Wellness",
        "company_domain": "classpass.com",  # Fallback for demo - original was zenithyoga.my
        "context_id": "ad_003_loyalty",
        "source_visual_url": "https://placehold.co/1200x628/E1F0FD/222222?text=Digital+Loyalty+App",
        "lead_name": "Priya Nair",
        "business_operation": "Services",
        "merchant_current_platform": "ClassPass",
        "business_store_name": "Zenith Yoga Studio",
        "average_revenue_month": 28000,
        "phone": "60123344556",
        "average_orders_per_day": 12,
        "basket_size_order": 75,
        "email": "priya.nair@zenithyoga.my",
        "existing_pos_system": "None",
        "industry": "Services",
        "sub_industry": "Health & Wellness",
        "when_need_pos": "In 1 month",
        "num_outlets": 1,
        "contact_role": "Founder",
        "preferred_language": "English"
    },
    {
        "lead_id": "00Q8d000002bY1hEAF",
        "company_name": "Papa's Kitchen PJ",
        "company_domain": "github.com",  # Fallback for demo - original was papaskitchen.com
        "context_id": "ad_001_pos",
        "source_visual_url": "https://placehold.co/1200x628/EFEFEF/333333?text=Modern+Cloud+POS",
        "lead_name": "Chef Ismail",
        "business_operation": "F&B",
        "merchant_current_platform": "None",
        "business_store_name": "Papa's Kitchen",
        "average_revenue_month": 75000,
        "phone": "60191112223",
        "average_orders_per_day": 60,
        "basket_size_order": 42,
        "email": "chef.ismail@papaskitchen.com",
        "existing_pos_system": "iPay88",
        "industry": "Food & Beverage",
        "sub_industry": "Restaurant",
        "when_need_pos": "In 3 months",
        "num_outlets": 1,
        "contact_role": "Owner",
        "preferred_language": "Bahasa Malaysia"
    },
    {
        "lead_id": "00Q8d000002bY1iEAF",
        "company_name": "The Pantry Grocer Sdn Bhd",
        "company_domain": "thepantry.com.my",  # Keep original - this works
        "context_id": "ad_002_ecommerce",
        "source_visual_url": "https://placehold.co/1200x628/FDF8E1/444444?text=Your+Online+Store",
        "lead_name": "David Cheah",
        "business_operation": "Retail",
        "merchant_current_platform": "None",
        "business_store_name": "The Pantry Grocer",
        "average_revenue_month": 150000,
        "phone": "60145556677",
        "average_orders_per_day": 100,
        "basket_size_order": 50,
        "email": "david.cheah@thepantry.com.my",
        "existing_pos_system": "Generic PC-based POS",
        "industry": "Retail",
        "sub_industry": "Grocery / Specialty Food",
        "when_need_pos": "Immediately",
        "num_outlets": 1,
        "contact_role": "Director",
        "preferred_language": "English"
    },
    {
        "lead_id": "00Q8d000002bY1jEAF",
        "company_name": "Kayu Living Concepts",
        "company_domain": "google.com",  # Fallback for demo - original was kayuhome.my
        "context_id": "ad_002_ecommerce", 
        "source_visual_url": "https://placehold.co/1200x628/FDF8E1/444444?text=Your+Online+Store",
        "lead_name": "Michelle Yeoh",
        "business_operation": "Retail",
        "merchant_current_platform": "Instagram Shop",
        "business_store_name": "Kayu Home Decor",
        "average_revenue_month": 55000,
        "phone": "60187654321",
        "average_orders_per_day": 8,
        "basket_size_order": 225,
        "email": "michelle.y@kayuhome.my",
        "existing_pos_system": "None",
        "industry": "Retail",
        "sub_industry": "Home & Living",
        "when_need_pos": "Researching options",
        "num_outlets": 1,
        "contact_role": "Owner",
        "preferred_language": "Mandarin"
    }
]

# Enhanced business intelligence mapping
BUSINESS_INTELLIGENCE = {
    "Kopi Kulture Sdn Bhd": {
        "business_type": "F&B - Cafe",
        "location": "Malaysia", 
        "pain_points": ["Manual cash drawer inefficiency", "GrabFood integration issues", "Peak hour queue management"],
        "revenue_segment": "Medium",
        "urgency": "High",
        "decision_maker": "Owner",
        "quick_replies": [
            "Manual cash drawer is too slow",
            "Need better GrabFood integration",
            "80 orders daily getting chaotic"
        ]
    },
    "The Daily Bakehouse": {
        "business_type": "F&B - Bakery",
        "location": "Malaysia",
        "pain_points": ["No POS system", "Instagram order management", "Customer loyalty tracking"],
        "revenue_segment": "Small-Medium",
        "urgency": "Immediate",
        "decision_maker": "Founder",
        "quick_replies": [
            "Managing Instagram orders manually",
            "Need loyalty program badly",
            "Want to track regular customers"
        ]
    },
    "NJ Maju Enterprise": {
        "business_type": "F&B - Quick Service Restaurant",
        "location": "Malaysia",
        "pain_points": ["Current POS limitations", "Multi-outlet management", "FoodPanda integration"],
        "revenue_segment": "Large",
        "urgency": "Medium",
        "decision_maker": "Operations Manager",
        "quick_replies": [
            "Slurp POS not meeting needs",
            "Managing 3 outlets difficult",
            "250 orders daily across locations"
        ]
    },
    "Lila & Co Apparel": {
        "business_type": "Retail - Fashion & Apparel",
        "location": "Malaysia",
        "pain_points": ["Shopify integration with physical store", "Inventory sync", "Higher basket value management"],
        "revenue_segment": "Medium",
        "urgency": "Low",
        "decision_maker": "Owner",
        "quick_replies": [
            "Already on Shopify POS",
            "Researching better options",
            "Need seamless online-offline sync"
        ]
    },
    "Boba Bliss Holdings": {
        "business_type": "F&B - Beverage Kiosk",
        "location": "Petaling Jaya, Malaysia", 
        "pain_points": ["Existing StoreHub user seeking upgrades", "Multi-outlet coordination", "Loyalty program enhancement"],
        "revenue_segment": "Large",
        "urgency": "Medium",
        "decision_maker": "Co-Founder",
        "quick_replies": [
            "Already using StoreHub",
            "Want enhanced loyalty features",
            "2 outlets need better coordination"
        ]
    },
    "Chapter One Ventures": {
        "business_type": "Retail - Books & Stationery", 
        "location": "Malaysia",
        "pain_points": ["Manual cash drawer", "Wix website integration", "Low order frequency"],
        "revenue_segment": "Small-Medium",
        "urgency": "Immediate",
        "decision_maker": "Manager",
        "quick_replies": [
            "Manual cash drawer inefficient",
            "Want to integrate with Wix site",
            "10 orders daily but growing"
        ]
    },
    "Zenith Wellness": {
        "business_type": "Services - Health & Wellness",
        "location": "Malaysia",
        "pain_points": ["No POS system", "ClassPass integration", "Service-based billing"],
        "revenue_segment": "Small-Medium",
        "urgency": "High",
        "decision_maker": "Founder",
        "quick_replies": [
            "No POS system currently",
            "Work with ClassPass bookings",
            "Need service billing solution"
        ]
    },
    "Papa's Kitchen PJ": {
        "business_type": "F&B - Restaurant",
        "location": "Malaysia",
        "pain_points": ["iPay88 payment limitations", "No online ordering", "Order management efficiency"],
        "revenue_segment": "Large",
        "urgency": "Medium",
        "decision_maker": "Owner",
        "quick_replies": [
            "iPay88 has limitations",
            "No online ordering system",
            "60 daily orders need better flow"
        ]
    },
    "The Pantry Grocer Sdn Bhd": {
        "business_type": "Retail - Grocery",
        "location": "Malaysia",
        "pain_points": ["Generic PC POS limitations", "No online platform", "High volume operations"],
        "revenue_segment": "Enterprise",
        "urgency": "Immediate",
        "decision_maker": "Director",
        "quick_replies": [
            "Current PC POS is outdated",
            "Need online grocery platform",
            "100 orders daily and growing"
        ]
    },
    "Kayu Living Concepts": {
        "business_type": "Retail - Home & Living",
        "location": "Malaysia", 
        "pain_points": ["Instagram Shop limitations", "No POS system", "High-value transactions"],
        "revenue_segment": "Large",
        "urgency": "Low",
        "decision_maker": "Owner",
        "quick_replies": [
            "Only using Instagram Shop",
            "No proper POS system",
            "High-value orders need tracking"
        ]
    }
}

# Ad context definitions (enhanced)
AD_CONTEXTS = {
    "ad_001_pos": {
        "title": "Modern Cloud POS System",
        "focus": "Point of Sale efficiency", 
        "pain_points": ["slow checkout", "manual cash register", "payment processing"],
        "solution_angle": "streamlined POS operations",
        "target_businesses": ["cafes", "restaurants", "QSR"]
    },
    "ad_002_ecommerce": {
        "title": "Complete E-commerce Solution",
        "focus": "Online store setup",
        "pain_points": ["no online presence", "limited reach", "inventory management"], 
        "solution_angle": "omnichannel retail experience",
        "target_businesses": ["fashion", "books", "grocery", "home decor"]
    },
    "ad_003_loyalty": {
        "title": "Digital Loyalty Program", 
        "focus": "Customer retention",
        "pain_points": ["customer retention", "repeat business", "loyalty tracking"],
        "solution_angle": "customer lifetime value optimization",
        "target_businesses": ["bakery", "beverage", "wellness"]
    }
}

def get_lead_context(lead_id: str) -> Optional[Dict]:
    """Get comprehensive context for a lead including business intelligence and ad context"""
    
    # Find the lead data
    lead_data = None
    for lead in MOCK_LEADS_DATA:
        if lead["lead_id"] == lead_id:
            lead_data = lead
            break
    
    if not lead_data:
        return None
    
    # Get business intelligence
    company_name = lead_data["company_name"] 
    business_intel = BUSINESS_INTELLIGENCE.get(company_name, {})
    
    # Get ad context
    context_id = lead_data["context_id"]
    ad_context = AD_CONTEXTS.get(context_id, {})
    
    # Enhanced context with CSV data
    enhanced_context = {
        "lead_data": lead_data,
        "business_intel": business_intel, 
        "ad_context": ad_context,
        "personalized_context": f"This lead {lead_data.get('lead_name', 'from')} from {company_name} ({lead_data.get('sub_industry', 'business')}) clicked on our '{ad_context.get('title', 'unknown')}' ad. They generate RM{lead_data.get('average_revenue_month', 0):,}/month with {lead_data.get('average_orders_per_day', 0)} daily orders. Current system: {lead_data.get('existing_pos_system', 'Unknown')}. Timeline: {lead_data.get('when_need_pos', 'Not specified')}.",
        "financial_profile": {
            "monthly_revenue": lead_data.get("average_revenue_month", 0),
            "daily_orders": lead_data.get("average_orders_per_day", 0),
            "basket_size": lead_data.get("basket_size_order", 0),
            "annual_revenue_estimate": lead_data.get("average_revenue_month", 0) * 12
        },
        "contact_info": {
            "name": lead_data.get("lead_name", ""),
            "role": lead_data.get("contact_role", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", ""),
            "preferred_language": lead_data.get("preferred_language", "English")
        },
        "operational_details": {
            "num_outlets": lead_data.get("num_outlets", 1),
            "current_platform": lead_data.get("merchant_current_platform", "None"),
            "existing_pos": lead_data.get("existing_pos_system", "None"),
            "urgency": lead_data.get("when_need_pos", "Not specified")
        }
    }
    
    return enhanced_context

def get_contextual_quick_replies(lead_id: str, mei_last_message: str = "") -> List[str]:
    """Generate contextual quick replies based on lead's business context and Mei's last question (FALLBACK)"""
    
    # This is now primarily a fallback function when LLM generation fails
    # If Mei's last message contains specific questions, generate relevant responses
    if mei_last_message:
        mei_lower = mei_last_message.lower()
        
        # Question about business type/industry
        if any(word in mei_lower for word in ["business", "industry", "type", "running", "what do you"]):
            return [
                "We run a restaurant",
                "It's a retail store", 
                "Coffee shop business"
            ]
        
        # Questions about location
        elif any(word in mei_lower for word in ["location", "where", "based", "operating"]):
            return [
                "Kuala Lumpur area",
                "Selangor, Malaysia",
                "Petaling Jaya"
            ]
        
        # Questions about role/decision making
        elif any(word in mei_lower for word in ["owner", "manager", "decision", "charge", "responsible"]):
            return [
                "Yes, I'm the owner",
                "I'm the manager",
                "I make decisions"
            ]
        
        # Questions about current systems/problems
        elif any(word in mei_lower for word in ["current", "system", "problem", "challenge", "difficulty", "pos", "setup"]):
            return [
                "Manual cash register",
                "No inventory system", 
                "Payment is slow"
            ]
        
        # Questions about goals/achievements
        elif any(word in mei_lower for word in ["achieve", "looking", "hoping", "goal", "improve", "want"]):
            return [
                "Speed up service",
                "Better tracking",
                "Grow sales"
            ]
        
        # Questions about staff/team size
        elif any(word in mei_lower for word in ["staff", "employee", "team", "people", "work"]):
            return [
                "3-4 staff members",
                "Just me and partner",
                "5 employees total"
            ]
        
        # Questions about sales volume/customers
        elif any(word in mei_lower for word in ["sales", "customer", "daily", "volume", "busy"]):
            return [
                "100+ customers daily",
                "RM1000-2000 sales",
                "Very busy lunch"
            ]
        
        # Questions about timeline/urgency
        elif any(word in mei_lower for word in ["when", "timeline", "urgent", "soon", "planning"]):
            return [
                "As soon as possible",
                "Within next month",
                "This quarter"
            ]
        
        # Questions about budget/pricing
        elif any(word in mei_lower for word in ["budget", "cost", "price", "afford", "expensive"]):
            return [
                "What's monthly cost?",
                "Budget under RM500",
                "Need affordable option"
            ]
        
        # Questions about demo/meeting interest
        elif any(word in mei_lower for word in ["demo", "meeting", "show", "presentation", "see how"]):
            return [
                "Yes, show demo",
                "Can we meet?",
                "Online demo preferred"
            ]
        
        # Questions about specific features
        elif any(word in mei_lower for word in ["feature", "function", "integrate", "support"]):
            return [
                "Need inventory tracking",
                "Want online ordering",
                "Kitchen display important"
            ]
    
    # Fallback: Use business-specific context if available
    context = get_lead_context(lead_id)
    if not context:
        return [
            "Tell me more",
            "I'm interested", 
            "Show me options"
        ]
    
    # Use top 3 business-specific quick replies as fallback
    business_replies = context["business_intel"].get("quick_replies", [])
    if business_replies:
        return business_replies[:3]
    
    # Final default responses
    return [
        "I need help",
        "Tell me more",
        "Show me demo"
    ]

def get_all_leads() -> List[Dict]:
    """Get all mock leads for selection interface"""
    return MOCK_LEADS_DATA 