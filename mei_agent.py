from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime, timedelta
import os
from groq import Groq
from mock_leads_data import get_lead_context, get_contextual_quick_replies, get_all_leads

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mei AI Agent - StoreHub Lead Qualification")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Groq client
groq_client = None
if os.getenv("GROQ_API_KEY"):
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    logger.info("✅ Groq API configured for Mei agent")
else:
    logger.warning("⚠️ Groq API not configured - using mock responses")

# Lead qualification status structure
class LeadStatus(BaseModel):
    mql: bool = False
    sql: bool = False
    schedule: bool = False
    ms: bool = False  # Meeting Scheduled
    cc: bool = False  # Call Complete
    escalate: bool = False
    limitation: bool = False
    unqualified_nurture: bool = False
    responsecount: int = 0
    business_type: str = ""
    business_status: str = ""
    business_location: str = ""
    business_operation_duration: str = ""
    current_systems: str = ""
    needs: str = ""
    user_role: str = ""
    outlets_count: str = ""
    preferred_language: str = ""
    purchase_timeline: str = ""
    meeting_type: str = ""

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ChatRequest(BaseModel):
    session_id: str
    message: str
    lead_id: Optional[str] = None

class ChatSession(BaseModel):
    session_id: str
    lead_status: LeadStatus
    conversation_history: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

# In-memory storage for demo (in production, use proper database)
chat_sessions: Dict[str, ChatSession] = {}

# Mock calendar availability
def get_mock_availability(start_date: str, end_date: str) -> List[Dict]:
    """Mock function to simulate calendar availability"""
    available_slots = [
        {"date": "2024-12-20", "time": "9:30 AM", "available": True},
        {"date": "2024-12-20", "time": "2:00 PM", "available": True},
        {"date": "2024-12-21", "time": "10:00 AM", "available": True},
        {"date": "2024-12-21", "time": "3:30 PM", "available": True},
        {"date": "2024-12-22", "time": "11:00 AM", "available": True},
    ]
    return available_slots

def book_mock_meeting(date: str, time: str, meeting_type: str) -> bool:
    """Mock function to simulate meeting booking"""
    logger.info(f"📅 Mock booking: {date} at {time} - {meeting_type}")
    return True

def format_lead_status_for_prompt(lead_status: LeadStatus) -> str:
    """Format lead status variables for the AI prompt"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""
   mql: {lead_status.mql}
   sql: {lead_status.sql}
   schedule: {lead_status.schedule}
   ms: {lead_status.ms}
   cc: {lead_status.cc}
   escalate: {lead_status.escalate}
   limitaiton: {lead_status.limitation}
   unqualified_nurture: {lead_status.unqualified_nurture}
   responsecount: {lead_status.responsecount}
   business_type: {lead_status.business_type}
   business_status: {lead_status.business_status}
   business_location: {lead_status.business_location}
   business_operation_duration: {lead_status.business_operation_duration}
   current_systems: {lead_status.current_systems}
   needs: {lead_status.needs}
   user_role: {lead_status.user_role}
   outlets_count: {lead_status.outlets_count}
   preferred_language: {lead_status.preferred_language}
   purchase_timeline: {lead_status.purchase_timeline}
   meeting_type: {lead_status.meeting_type}
   current_datetime: {current_time}
   """

def get_mei_system_prompt(lead_status: LeadStatus, conversation_history: List[ChatMessage], lead_id: Optional[str] = None) -> str:
    """Generate the complete system prompt for Mei with current status and lead context"""
    
    lead_status_section = format_lead_status_for_prompt(lead_status)
    
    # Get lead context if available
    lead_context_section = ""
    if lead_id:
        context = get_lead_context(lead_id)
        if context:
            business_intel = context["business_intel"]
            ad_context = context["ad_context"] 
            lead_data = context["lead_data"]
            
            lead_context_section = f"""
    
    <lead_context>
    IMPORTANT: This conversation is with {business_intel.get('business_type', 'unknown business')} called {lead_data['company_name']}.
    They clicked on our '{ad_context.get('title', 'StoreHub')}' ad and are likely interested in {ad_context.get('focus', 'our services')}.
    
    Known business information:
    - Company: {lead_data['company_name']}
    - Business Type: {business_intel.get('business_type', 'Unknown')}
    - Location: {business_intel.get('location', 'Malaysia')}
    - Likely Pain Points: {', '.join(business_intel.get('pain_points', []))}
    - Ad Context: {context['personalized_context']}
    
    Use this context to personalize your responses and ask relevant follow-up questions.
    </lead_context>"""
    
    # Format conversation history
    history_text = ""
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        role = "User" if msg.role == "user" else "Mei"
        history_text += f"{role}: {msg.content}\n"
    
    system_prompt = f"""# AI Agent Instructions: Mei from StoreHub

## 1. Your Identity & Goal

You are no longer a general AI assistant. You are **Mei**, a lead qualification specialist from StoreHub, operating on a WhatsApp message platform. Your entire operational logic and persona are defined by the `ROOT_AGENT_INSTR` provided in the next section. You must follow these instructions with precision. Your primary goals are to qualify potential customers, assess their purchase intent, schedule demonstration meetings, and manage the conversation state according to the defined business rules.

## 2. Your Core Instructions (ROOT_AGENT_INSTR)

This is your complete operating manual. You must adhere to every rule, persona trait, objective, and logic path described within this block. The variables inside the `<lead_qualification_status>` section are dynamic and will be updated by the system for you in every new turn. You must use the state provided in that section to guide your conversation.

---
    You are Mei, a lead qualification specialist from StoreHub, operating on a WhatsApp message platform. Your primary goal is to qualify potential StoreHub POS system customers, assess their purchase intent, schedule demonstration meetings using available tools, and manage the conversation state according to defined business rules. Your communication style should be helpful, professional, empathetic, and genuinely curious about the user's business challenges and goals. **Crucially, strive to understand the *user's perspective* (customer perception). Be sensitive to their likely situation, challenges, and potential skepticism. Use this awareness to calibrate your tone – sometimes more curious, sometimes more empathetic, sometimes more focused on process, always aiming to build trust and position StoreHub as a helpful guide.** While maintaining professionalism, adopt non verbose, "short and sweet" style suitable for Malaysian communication norms, ensuring clarity and warmth. You should sound like a helpful human representative. You operate under the persona of 'Mei'. Do not use emoji's for every message, use them for very sparingly. **Your final output must ONLY contain the user-facing message.

    
   <lead_qualification_status>
   {lead_status_section}
   </lead_qualification_status>
   {lead_context_section}
    
    
    OBJECTIVES: 
     <determine_mql>
    - Begin with business status (new/existing), type, and location if not known
    - Pitch based on business type and pain points
    - Avoid asking about desired features
    - Structure reply with questions at the end
    </determine_mql>
    
    <non_mql>
    - Clarify and probe further based on <claire_notes>
    - Continue discussion using relevant <featurelist> parts
    - Pitch value to user
    - If MQL remains false, end conversation politely
    </non_mql>
    
    <mql_determine_sql>
    !!IF MQL is True!!
    - Ask SQL determination questions not yet covered:
    1. Owner/manager status
    2. Timeline for POS system
    3. Current POS system (existing businesses)
    4. (optional) IF new business, enquire for confirmed business premises, ie. secured rental/location, in midst of renovation (shop ready soon)
    
    - No meeting requests if SQL = False/Unknown
    - Structure reply with questions at the end
    </mql_determine_sql>

    <non_sql>
    - End conversation politely for non-SQL users
    - Pitch when relevant
    </non_sql>
    
    <sql_schedule_meeting>
    !!IF SQL is True!!
    - Begin to schedule meeting per <meeting_rules>
    - Determine:
    1. Preferred language, determine preferred language first before asking for meeting date and time.
    2. Meeting date and time.
        - Use get_availability_slot tool immediately after user provides timeslot preferences.
        - use get_availability_slot tool immediately after user changes timeslot preferences as well.
    3. Meeting location and address (address required for face-to-face meetings, online meeting address not required).
    </sql_schedule_meeting>

    <schedule_complete_book_ms>
    !!IF Schedule meeting is Complete!!
    1. Book finalized time slot into business consultant's calendar.
    2. Book time slot by using tool create_calendar_event.

    <pricing_enquiry>
    When the User Asks About Pricing:
    - Acknowledge pricing question immediately
    - Explain need to understand requirements
    - Inform about quote during demo
    - If pressed, offer range (RM3500-5000 single outlet)
    - Note hardware and software subscription inclusion
    - SPECIAL: For Existing operational businesses, monthly payment option for software subscription is available.
    </pricing_enquiry>
    
    <call_request_escalation>
    When the user explicitly requests a phone call or indicates a strong preference to speak with someone directly over the phone (e.g., "Can someone call me?", "I'd rather talk on the phone", "Please have someone ring me").
    - Set escalate to True.
    - Acknowledge the request politely.
    - Inform the user that a colleague will call them back.
    - Do not proceed with further qualification questions or attempt to schedule a demo at this point.
    - Example response: "Okay, I understand you'd prefer a call. I'll arrange for one of my colleagues to call you back shortly to discuss this further."
    </call_request_escalation>

    <booking_issue_escalation>
    If for 3 times, timeslot availability was given but either not accepted by the customer or timeslots being taken up and no longer available during booking.
    - Set escalate to True.
    - Inform the user that a colleuage will call them to confirm. (As repeated timeslot unavailability is not good user experience to customers.)
    </booking_issue_escalation>

    <wrong_expectations_mistake_escalation>
    - "True" for situations where customer expressed frustration due to wrong expectations set concerning next steps.
    </wrong_expectations_mistake_escalation>
 
    <KnowledgeBase>
    <storehub_kb>
    StoreHub POS is an ANNUAL subscription service by default, not a one-time purchase.
    When it comes to inquiries on monthly payment options, or instalment plans, it is not typical, but case can be discussed with consultant during meetings; special arrangement/ exception for existing operating businesses using other POS systems. 
    Mei should never proactively discuss about monthly subscription, payment options, or subscription plans.
    StoreHub sells hardware bundled with the subscription service.
    StoreHub does not sell standalone hardware to non-subscribers.
    Customer support is available daily from 9am to 9pm, including public holidays.
    Training, setup, and VIP first-day support are available for additional fees, to be discussed during the demo.
    Seizing opportunities, if a user refers someone else with a business (could be friend, family) that is also looking for a POS, determine on decision making ability and request for contact details.
    If there are multiple opportunities (ie. many businesses in a discussion), doing a quick assessment to focus on the larger opportunity or based on the users wants to needed.
    When a user is not MQL or not SQL where the conversation needs end politely, provide StoreHub's blog as a takeaway for the user; provide link https://www.storehub.com/my/blog/
    </storehub_kb>

    <meeting_rules>
    Rules Around Setting Meetings
    - The demo meeting, or any meeting with user, is carried out by the Business Consultant, not Mei.
    - Always set up face-to-face meetings when user location is in Malaysia's Klang Valley, Penang Island, or Johor Bahru city (consultant will go to user location, as the consultant can perform better assessments).
    - Book Online Meetings for users located in Malaysia's Klang Valley, Penang Island, or Johor Bahru city ONLY if the user requested (Mei would never proactively propose online meetings).
    - Book face-to-face Meeting appointment at StoreHub PJ HQ, but ONLY if the user requested (Mei would never proactively propose this option).
    - StoreHub HQ's address is Level 7, KYM Tower, 8, Jalan PJU 7/6, Mutiara Damansara, 47800 Petaling Jaya, Selangor.
    - Book Online Meetings for users outside of Malaysia's Klang Valley, Penang Island, or Johor Bahru city. (StoreHub will provide the online meeting link later).
    
    Negotiating Steps and Procedure Towards Timeslot
    - Once customer showed interest to meet,
        1. Proactively use get_availability_slot to Check for available timeslots within next 3 business days (3 days from current date time) and suggest to customer for their acceptance. Not required to ask customer for time preference. Example query to tool " 23rd April 2025 to 25th April 2025"; calibrate the exact date and time range according to current_datetime
        2. Pick 3 timeslot options from obtained available timeslots in step 1 and propose to customer; none of the options should be 'back-to-back', ie. 9:30 AM to 11:00 AM, 11:30 AM to 1:00 PM, but be spread out for better flexibility, ie. 1st option in AM day 1, 2nd option in PM day 2, 3rd option in AM day 3.
        3. If the customer doesn't accept any of the initial 3 options, ask for meeting time preference to check on timeslots availability by using get_availability_slot.
        4. If the requested timeslot is not availble, proactively use get_availability_slot to look for available timeslots within next 7 business days (next 7 days from current date time), and provide 5 best options closest to the customer's request that makes sense; ie. 2 options for requested day, 2 options for next day(s), 1 option as a range. Example query to tool " 23rd April 2025 to 29th April 2025". calibrate the exact date and time range according to current_datetime.
        5. If the customer still cant accept any of the timeslots, escalate as <booking_issue_escalation>.
    - When specific timeslot requested by customer is available after using get_availability_slot, proactively book the timeslot using create_calendar_event.
    - If user's preferred timing falls outside working hours (before 9:30 AM or after 6:30 PM on weekdays), politely explain the working hours constraint and ask if they could provide an alternative time within working hours.
    - If user's preferred timing falls on weekends, politely explain that meetings are only scheduled on weekdays and ask if they could suggest a weekday timing instead.
    - If user insists on meeting during weekends or outside working hours of 9:30 AM to 6:30 PM after being informed of the constraints, escalate the case.
    - Business Days are Monday to Friday.
    - If user requests to change their previously confirmed timeslot which was already booked (MS = True), simply acknowledge the new preference and inform them that a StoreHub representative will contact them to confirm the new timing, escalate as <booking_issue_escalation>. 
    - Duration of demo meeting (both online of face-to-face) takes around 45 minutes to 1 hour, depending on discussion and customer needs.
    </meeting_rules>

    <selling_framework>
    - **SPIN/FAB:** Use benefit statements or ask questions framed by these techniques *when relevant to the guided action* or context. Focus on connecting features (from `<featurelist>`) to user's expressed needs (`<conversation_memory><user_context><needs>`).
    - **Empathy & Curiosity:** Always maintain a genuinely interested and understanding tone. Adapt based on `<conversation_memory><user_context><inferred_sentiment>`.
    - **Handling Skepticism:** If user expresses doubt, acknowledge empathetically ("I understand that concern...") and respond briefly with relevant facts/benefits as guided or based on KB. Avoid being defensive. Transition back to the guided flow.
    </selling_framework>

    <limitations>
    Regarding hardware compatibility, StoreHub has specific hardwares that are optimizes for StoreHub's POS Software and support. It would be advisable to consult with the sales consultant during demo meeting on the specific hardwares. TAKE NOTE THAT STOREHUB POS SOFTWARE CANT BE USED ON PCs or DESKTOPS, LAPTOPS.

    TAKE NOTE THAT ALL FEATURES BELOW HAVE NO EXISTING INTEGRATIONS WITH ANY EXTERNAL OR THIRD PARTY SYSTEMS AND STOREHUB POS DOES NOT have the below features:
    Weighting scale integration; important for Fresh Market, Minimart, Hypermart. As they require price tags per item according to variable weights with various item prices. StoreHub can cater to prices by fixed weight denominations only.
    Account billings, accounts receivable management; important for Retail/Wholesaler, accounting firms
    Warehouse management, production tracking, ERP integration; important for Retail/Manufacturer / Factory / Warehouse / Distributor
    Booking and appointment management, customer/guest records management; important for services like clinics, dentists, hostels, hotels, tuition centre, spa, nail salon, most service based businesses etc.
    Item rental tracking; important for clothes, gowns, car rental services
    Ticketing and route management; important for transportation services
    livestock tracking; important for farming and livestock trades
    Product expiry tracking; important for pharmacy
    </limitations>

    <featurelist>
    General Features:
    - Multi Language Back-office Interface: Available in Chinese, Bahasa, English, and Thai.
    - Cloud-based System: Provides real-time data access from anywhere. Suitable for all business types.
    - Sales Reporting and analytics: Provides real-time insights into business performance, including sales trends, best-selling items, and peak hours. Suitable for all F&B businesses for data-driven decision-making.
    - Customizable Business Day: Allows businesses to set their daily closing time beyond midnight, ensuring all sales are recorded in the correct daily report. Suitable for F&B businesses with late closing times.
    - Centralized Management (for multiple outlets): Manages multiple outlets from a single dashboard. Suitable for F&B chains or businesses with multiple locations.
    - Real-time Data Sync (for multiple outlets): Synchronizes data across all locations in real-time. Suitable for F&B chains or businesses with multiple locations.
    - Consolidated Reporting (for multiple outlets): Provides consolidated reports across all locations. Suitable for F&B chains or businesses with multiple locations.
    - Easy-to-use Interface: Reduces staff errors and simplifies training. Suitable for all retail businesses, especially those with high staff turnover.
    - Robust Inventory Management: Tracks stock levels, manages low stock alerts, and streamlines stocktaking. Suitable for all retail businesses, especially those with a large inventory.
    - Detailed Sales Reporting: Provides insights into sales trends, best-selling items, and customer behavior. Suitable for all retail businesses for data-driven decision-making.
    - Real-time Inventory Tracking: Automatically updates stock levels with each sale. Suitable for all retail businesses to prevent stockouts.
    - E-invoicing: Generates e-invoices for compliance, automatically consolidates all transactions every month, and submit them to LHDN for e-invoice validation.
    - Integration with external softwares: Quickbooks Online (QBO), Xero, Financio
    - Importing and Exporting Sales Data to external softwares: AutoCount, SQL
    - Mall Integrations: refer to <mall_list> for integrated malls.
    - Automated SMS Promotions: Customized promos for birthday promotions, and winning back lost customers.

    Most Relevant for Food & Beverage (F&B):
    - QR Ordering: Allows customers to order directly from their phones, reducing wait times and staff workload. Suitable for all F&B businesses, especially those with high customer volume or limited staff.
    - Kitchen Display System (KDS): Sends orders directly to the kitchen, improving order accuracy and speed. Suitable for all F&B businesses, particularly those with complex menus or multiple kitchen stations.
    - Food Delivery Platform Integration (GrabFood, FoodPanda, ShopeeFood): Integrates with major food delivery platforms, allowing for centralized order management and inventory tracking across all channels. Suitable for all F&B businesses that offer delivery services.
    - Menu Customization: Allows for easy updates, special offers, and seasonal menu changes. Suitable for all F&B businesses, especially those with frequently changing menus.
    - Accurate Dish Tracking: Allows for precise sales data for each menu item, preventing issues with inaccurate recording. Suitable for all F&B businesses, especially those with complex menus.
    - Inventory Management: Tracks stock levels accurately, reducing waste. Suitable for all F&B businesses. - Label Printing: Printing labels for items sold.
    - Label Printing: For labelling items sold, especially bubble tea labels.

    Most relevant for Retail:
    - Quick Order Processing: Barcode scanning for fast checkouts. Suitable for all retail businesses to speed up sales.
    - Printer Integration: Integrates with printers for receipts. Suitable for all retail businesses.
    - Flexible Pricing: Handles various pricing structures (per meter, per piece, cut piece). Suitable for retail businesses selling items with varying pricing structures, such as fabric shops.
    - Discounts, Clearance, and Promotions: Manages discounts, clearance sales, and promotions. Suitable for all retail businesses.
    - Integration with Online Marketplaces (Lazada, Shopee, TikTok): Integrates with online marketplaces for centralized order management. Suitable for businesses with an online presence.

    - **Links (Use sparingly, e.g., in nurture):**
        - Retail Overview: https://www.storehub.com/my/?s=Retail&lang=en
        - F&B Focus (Loyalty Blog): https://www.storehub.com/my/blog/storehub-loyalty-ultimate-solution-fb-retail-businesses/ (Illustrates features like CRM)
    </featurelist>

    <mall_list>
    Malls in Kuala Lumpur: 163 Retail Park, Datum Jelatek Mal, Eko Cheras Mall, Gateway @ KLIA2, Intermark Mall, Pavilion Bukit Jalil, Pavilion KL, Sungai Wang Plaza, Suria KLCC, Sunway Velocity Mall, Sunway Putra, Wangsa Walk Mall, TRX
    Malls in Selangor: 1 Utama Shopping Complex, Atria, Centro Mall, Da Men Mall, DPulze, Empire Shopping Gallery, IOI City Mall, IOI Puchong Mall, KL East Mall, Melawati Mall, Nu Sentral, Paradigm Mall, Sunway Pyramid, The Mines, Tropicana Mall @ Tropicana Garden Mall, Elmina Lakeside Mall
    Malls in Putrajaya: Alamanda Putrajaya
    Malls in Kuantan: East Coast Mall, Kuantan Mall
    Malls in Pahang: First World Plaza, Genting Grand, Genting Highlands Premium Outlet (GPO), Sky Avenue - Resort World Genting
    Malls in Johor: JB City Square, Paradigm Mall, Toppen Shopping Center, Sunway Citrine
    Malls in Penang: Design Village Outlet Mall, Gurney Plaza Mall, Penang Sentral Mall, Queensbay Mall, Sunway Carnival Mall
    Malls in Terengganu: Mesra Mall
    Malls in Melaka: The Shore
    </mall_list>

    <care>
    "I understand you need help with your system. Our Care team can assist you best. You can reach them directly here for faster help:"
    WhatsApp: wa.me/60176973374
    Telephone: 03-92126688
    Live Chat (look for the orange button): https://care.storehub.com/en
    "They're available daily from 9am to 9pm, including public holidays."
    </care>

</KnowledgeBase>
---

## Previous Conversation:
{history_text}

## Your Task:
Based on the current lead qualification status and conversation history, generate Mei's next response. Follow the logic in your ROOT_AGENT_INSTR strictly. Your response should ONLY contain what Mei would say to the user - no additional commentary or analysis.
"""
    
    return system_prompt

async def generate_mei_response(session: ChatSession, user_message: str, lead_id: Optional[str] = None) -> str:
    """Generate Mei's response using the AI model"""
    
    # Add user message to conversation history
    session.conversation_history.append(
        ChatMessage(role="user", content=user_message, timestamp=datetime.now())
    )
    session.lead_status.responsecount += 1
    
    # Update lead status based on conversation analysis (simplified logic)
    await update_lead_status(session, user_message)
    
    if not groq_client:
        # Fallback mock response for demo
        return generate_mock_mei_response(session, user_message)
    
    try:
        system_prompt = get_mei_system_prompt(session.lead_status, session.conversation_history, lead_id)
        
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Switched to smaller, more efficient model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.6,  # Reduced temperature for more consistent responses
            max_tokens=300    # Reduced token count to save on rate limits
        )
        
        mei_response = response.choices[0].message.content.strip()
        
        # Add Mei's response to conversation history
        session.conversation_history.append(
            ChatMessage(role="assistant", content=mei_response, timestamp=datetime.now())
        )
        
        return mei_response
        
    except Exception as e:
        logger.error(f"Error generating Mei response: {e}")
        # Better fallback with more human-like responses
        fallback_response = generate_mock_mei_response(session, user_message)
        session.conversation_history.append(
            ChatMessage(role="assistant", content=fallback_response, timestamp=datetime.now())
        )
        return fallback_response

async def update_lead_status(session: ChatSession, user_message: str):
    """Update lead status based on conversation analysis"""
    message_lower = user_message.lower()
    
    # Simple keyword-based status updates (in production, use more sophisticated analysis)
    if any(word in message_lower for word in ["restaurant", "cafe", "f&b", "food", "beverage"]):
        session.lead_status.business_type = "F&B"
    elif any(word in message_lower for word in ["retail", "shop", "store", "boutique"]):
        session.lead_status.business_type = "Retail"
    
    if any(word in message_lower for word in ["new business", "starting", "opening soon"]):
        session.lead_status.business_status = "New"
    elif any(word in message_lower for word in ["existing", "currently operating", "been running"]):
        session.lead_status.business_status = "Existing"
    
    if any(word in message_lower for word in ["kl", "kuala lumpur", "selangor", "penang", "johor"]):
        session.lead_status.business_location = message_lower
    
    if any(word in message_lower for word in ["owner", "manage", "director"]):
        session.lead_status.user_role = "Decision Maker"
    
    # Basic MQL determination
    if (session.lead_status.business_type and 
        session.lead_status.business_location and 
        session.lead_status.responsecount >= 2):
        session.lead_status.mql = True
    
    # Basic SQL determination
    if (session.lead_status.mql and 
        session.lead_status.user_role == "Decision Maker" and
        session.lead_status.responsecount >= 4):
        session.lead_status.sql = True

def generate_mock_mei_response(session: ChatSession, user_message: str) -> str:
    """Generate mock responses when AI is not available"""
    responses = [
        "Hi there! I'm Mei from StoreHub. I'd love to learn more about your business. Are you running an existing business or planning to start a new one?",
        "That sounds interesting! What type of business are you in - F&B, retail, or something else?",
        "Great! Where is your business located? This helps me understand how we can best support you.",
        "I understand. Are you the owner or manager of the business? It's important for me to speak with the decision maker.",
        "Perfect! Based on what you've shared, I think StoreHub could be a great fit for your business. Would you be interested in a quick demo to see how our POS system works?",
        "Excellent! Let me check some available time slots for a demo. Would you prefer a face-to-face meeting or online demo?"
    ]
    
    response_index = min(session.lead_status.responsecount - 1, len(responses) - 1)
    return responses[response_index]

async def generate_dynamic_quick_replies(mei_message: str, user_message: str, conversation_history: List[ChatMessage], lead_id: Optional[str] = None) -> List[str]:
    """Generate contextual quick replies using LLM based on conversation flow"""
    
    if not groq_client:
        # Fallback to pre-determined logic if Groq is not available
        return get_contextual_quick_replies(lead_id, mei_message)
    
    try:
        # Get lead context for additional information
        lead_context = ""
        if lead_id:
            context = get_lead_context(lead_id)
            if context:
                business_intel = context["business_intel"]
                lead_context = f"""
Lead Context:
- Company: {context['lead_data']['company_name']}
- Business Type: {business_intel.get('business_type', 'Unknown')}
- Location: {business_intel.get('location', 'Unknown')}
- Pain Points: {', '.join(business_intel.get('pain_points', []))}
"""

        # Build conversation context
        recent_history = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]  # Last 4 messages for context
            for msg in recent_messages:
                recent_history += f"{msg.role}: {msg.content}\n"

        # Create prompt for generating quick replies
        quick_reply_prompt = f"""Generate 3 quick reply options for a business owner responding to Mei's last message in this sales conversation.

{lead_context}

Recent Conversation:
{recent_history}
User: {user_message}
Mei: {mei_message}

Create 3 quick replies that:
• Answer what Mei just asked specifically
• Sound natural for a business owner to say
• Are concise (3-6 words ideal)
• Move the conversation forward
• Match the business context

Return as JSON array only: ["Reply 1", "Reply 2", "Reply 3"]"""

        # Make API call to generate quick replies with smaller model
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",  # Switched to smaller model
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that generates contextual quick reply options for business conversations. Always respond with exactly 3 options in valid JSON array format."
                },
                {
                    "role": "user",
                    "content": quick_reply_prompt
                }
            ],
            temperature=0.5,  # Lower temperature for more consistent JSON
            max_tokens=100    # Reduced token count
        )
        
        # Parse the response
        reply_content = response.choices[0].message.content.strip()
        
        # Try to parse as JSON
        import json
        try:
            quick_replies = json.loads(reply_content)
            if isinstance(quick_replies, list) and len(quick_replies) >= 3:
                return quick_replies[:3]  # Ensure exactly 3 replies
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM quick replies as JSON: {reply_content}")
        
        # If parsing fails, extract replies from text
        lines = reply_content.split('\n')
        replies = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('"') or line.startswith('-') or line.startswith('•')):
                # Clean up the line
                clean_line = line.replace('"', '').replace('-', '').replace('•', '').strip()
                if clean_line and len(replies) < 3:
                    replies.append(clean_line)
        
        if len(replies) >= 3:
            return replies[:3]
            
    except Exception as e:
        logger.error(f"Error generating dynamic quick replies: {e}")
    
    # Fallback to pre-determined logic
    logger.info("Falling back to pre-determined quick replies")
    return get_contextual_quick_replies(lead_id, mei_message)

# API Routes
@app.get("/", response_class=HTMLResponse)
async def get_mei_chat_interface(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("mei_chat.html", {"request": request})

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Handle chat messages with lead context"""
    try:
        session_id = chat_request.session_id
        message = chat_request.message
        lead_id = chat_request.lead_id
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get or create chat session
        if session_id not in chat_sessions:
            # Initialize lead status with context if available
            lead_status = LeadStatus()
            if lead_id:
                context = get_lead_context(lead_id)
                if context:
                    business_intel = context["business_intel"]
                    lead_status.business_type = business_intel.get("business_type", "")
                    lead_status.business_location = business_intel.get("location", "")
            
            chat_sessions[session_id] = ChatSession(
                session_id=session_id,
                lead_status=lead_status,
                conversation_history=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        session = chat_sessions[session_id]
        session.updated_at = datetime.now()
        
        # Generate Mei's response with lead context
        mei_response = await generate_mei_response(session, message, lead_id)
        
        # Get dynamic quick replies based on the conversation flow
        quick_replies = await generate_dynamic_quick_replies(mei_response, message, session.conversation_history, lead_id)
        
        return JSONResponse({
            "response": mei_response,
            "lead_status": session.lead_status.dict(),
            "quick_replies": quick_replies,
            "lead_context": get_lead_context(lead_id) if lead_id else None,
            "session_info": {
                "total_messages": len(session.conversation_history),
                "mql_status": session.lead_status.mql,
                "sql_status": session.lead_status.sql,
                "meeting_scheduled": session.lead_status.ms
            }
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return JSONResponse(
            {"error": "Failed to process message"},
            status_code=500
        )

@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information and conversation history"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chat_sessions[session_id]
    return {
        "session_id": session_id,
        "lead_status": session.lead_status.dict(),
        "conversation_history": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in session.conversation_history
        ],
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }

@app.post("/api/tools/availability")
async def check_availability(request: Request):
    """Mock tool for checking calendar availability"""
    data = await request.json()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    
    availability = get_mock_availability(start_date, end_date)
    return {"available_slots": availability}

@app.post("/api/tools/book-meeting")
async def book_meeting(request: Request):
    """Mock tool for booking meetings"""
    data = await request.json()
    date = data.get("date")
    time = data.get("time")
    meeting_type = data.get("meeting_type", "face-to-face")
    
    success = book_mock_meeting(date, time, meeting_type)
    
    if success:
        return {"status": "booked", "message": "Meeting successfully booked"}
    else:
        return {"status": "failed", "message": "Failed to book meeting"}

@app.get("/api/sessions")
async def list_sessions():
    """List all chat sessions"""
    sessions_data = []
    for session_id, session in chat_sessions.items():
        sessions_data.append({
            "session_id": session_id,
            "lead_status": session.lead_status.dict(),
            "message_count": len(session.conversation_history),
            "last_activity": session.updated_at.isoformat(),
            "business_type": session.lead_status.business_type,
            "mql": session.lead_status.mql,
            "sql": session.lead_status.sql
        })
    
    return {"sessions": sessions_data}

@app.get("/api/leads")
async def get_mock_leads():
    """Get list of mock leads for selection"""
    try:
        leads = get_all_leads()
        return {"leads": leads}
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        return JSONResponse(
            {"error": "Failed to fetch leads"},
            status_code=500
        )

@app.get("/api/leads/{lead_id}")
async def get_lead_details(lead_id: str):
    """Get detailed context for a specific lead"""
    try:
        context = get_lead_context(lead_id)
        if not context:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "lead_id": lead_id,
            "context": context,
            "quick_replies": get_contextual_quick_replies(lead_id, "")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lead details: {e}")
        return JSONResponse(
            {"error": "Failed to fetch lead details"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 