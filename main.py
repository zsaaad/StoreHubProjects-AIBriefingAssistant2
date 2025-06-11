# Step 2.1: Import necessary libraries at the top of this `main.py` file.
import requests
import json
from bs4 import BeautifulSoup
from groq import Groq
from fastapi import FastAPI
from pydantic import BaseModel
import config  # This imports the variables from your config.py

# Create FastAPI app instance
app = FastAPI(title="AI Pre-Call Briefing Assistant", description="Generate AI-powered sales briefings from company intelligence and lead context")

# Request model for the webhook endpoint
class WebhookRequest(BaseModel):
    company_domain: str
    context_id: str
    lead_id: str

# Step 2.2: Define the function stubs.
# We'll implement these one by one using Cursor's AI.

def get_company_intelligence(domain: str) -> str:
    """Gathers company info from their website and recent news."""
    try:
        # 1. Construct URL from domain
        if not domain.startswith('http'):
            url = f"https://{domain}"
        else:
            url = domain
        
        # 2. Scrape homepage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and limit to first 2000 characters
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        homepage_text = text[:2000]
        
        # 3. Get company name from domain
        company_name = domain.split('.')[0].replace('http://', '').replace('https://', '')
        
        # 4. Fetch news from NewsAPI
        news_titles = []
        if config.NEWS_API_KEY and config.NEWS_API_KEY != "YourNewsAPIKey":
            try:
                news_url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={config.NEWS_API_KEY}&pageSize=2&sortBy=publishedAt"
                news_response = requests.get(news_url, timeout=10)
                news_response.raise_for_status()
                news_data = news_response.json()
                
                for article in news_data.get('articles', []):
                    if article.get('title'):
                        news_titles.append(article['title'])
            except Exception as e:
                print(f"Error fetching news: {str(e)}")
                news_titles = ["News API unavailable"]
        else:
            news_titles = ["News API key not configured"]
        
        # 5. Combine information
        intelligence = f"""
        Company Website Content (first 2000 chars):
        {homepage_text}
        
        Recent News Headlines:
        {chr(10).join(f"- {title}" for title in news_titles)}
        """
        
        return intelligence.strip()
        
    except requests.RequestException as e:
        print(f"Error fetching website data: {str(e)}")
        return f"Error: Could not access website {domain}"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Error: Failed to gather intelligence for {domain}"

def get_lead_context(context_id: str) -> dict:
    """Retrieves lead-specific context from the mock database."""
    try:
        with open('mock_db.json', 'r') as file:
            data = json.load(file)
        
        for entry in data:
            if entry.get('context_id') == context_id:
                return entry
        
        print(f"Context ID '{context_id}' not found in mock database")
        return {}
    
    except FileNotFoundError:
        print("Error: mock_db.json file not found")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in mock_db.json")
        return {}
    except Exception as e:
        print(f"Error reading mock database: {str(e)}")
        return {}

def generate_ai_briefing(general_context: str, specific_context: str) -> str:
    """Sends the combined context to an LLM to generate a JSON briefing."""
    try:
        if not config.GROQ_API_KEY or config.GROQ_API_KEY == "gsk_YourGroqAPIKey":
            return json.dumps({
                "error": "GROQ API key not configured",
                "company_profile": "API key required",
                "key_updates": "API key required",
                "lead_angle": "API key required",
                "conversation_starters": "API key required",
                "potential_objections": "API key required"
            })
        
        # Initialize Groq client
        client = Groq(api_key=config.GROQ_API_KEY)
        
        # Construct detailed system prompt
        system_prompt = """You are an AI sales assistant that generates pre-call briefings for sales representatives. 
        You will receive general company information and specific lead context, then create a comprehensive JSON briefing.
        
        Your response MUST be a valid JSON object with exactly these keys:
        - "company_profile": A concise summary of the company's business, industry, and key characteristics
        - "key_updates": Recent news, developments, or changes at the company
        - "lead_angle": The specific value proposition or angle to pursue based on the lead context
        - "conversation_starters": 3-4 specific questions or topics to open the conversation
        - "potential_objections": 2-3 likely objections the prospect might have and how to address them
        
        Be specific, actionable, and focus on insights that will help the sales rep have a more effective conversation."""
        
        # Construct user prompt with context
        user_prompt = f"""
        Please generate a pre-call briefing based on the following information:
        
        GENERAL COMPANY INTELLIGENCE:
        {general_context}
        
        SPECIFIC LEAD CONTEXT:
        {specific_context}
        
        Generate a comprehensive JSON briefing that will help a sales representative prepare for their call with this prospect.
        """
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        # Extract and validate JSON response
        response_content = chat_completion.choices[0].message.content
        
        # Try to parse as JSON to validate
        parsed_json = json.loads(response_content)
        
        # Return the JSON string
        return response_content
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON response from AI: {str(e)}")
        return json.dumps({
            "error": "Invalid JSON response from AI",
            "company_profile": "Error generating briefing",
            "key_updates": "Error generating briefing", 
            "lead_angle": "Error generating briefing",
            "conversation_starters": "Error generating briefing",
            "potential_objections": "Error generating briefing"
        })
    except Exception as e:
        print(f"Error generating AI briefing: {str(e)}")
        return json.dumps({
            "error": f"Error: {str(e)}",
            "company_profile": "Error generating briefing",
            "key_updates": "Error generating briefing",
            "lead_angle": "Error generating briefing", 
            "conversation_starters": "Error generating briefing",
            "potential_objections": "Error generating briefing"
        })

def update_salesforce(lead_id: str, briefing: str):
    """Updates the lead record with the briefing. Uses local database for testing."""
    try:
        # Check if Salesforce credentials are configured for production use
        if (config.SALESFORCE_USERNAME and 
            config.SALESFORCE_PASSWORD and 
            config.SALESFORCE_SECURITY_TOKEN and
            config.SALESFORCE_USERNAME != "your.salesforce@email.com"):
            
            # Production Salesforce update
            from simple_salesforce import Salesforce
            
            sf = Salesforce(
                username=config.SALESFORCE_USERNAME,
                password=config.SALESFORCE_PASSWORD,
                security_token=config.SALESFORCE_SECURITY_TOKEN
            )
            
            update_result = sf.Lead.update(
                lead_id,
                {'AI_Pre_Call_Briefing__c': briefing}
            )
            
            print("--- SALESFORCE UPDATE SUCCESS ---")
            print(f"Updated Lead ID: {lead_id}")
            print(f"Update result: {update_result}")
            print("--- END SALESFORCE UPDATE ---")
            return
        
        # Use local database for testing
        print("--- LOCAL DATABASE UPDATE ---")
        
        # Read current leads database
        try:
            with open('leads_db.json', 'r') as file:
                leads_data = json.load(file)
        except FileNotFoundError:
            print("Warning: leads_db.json not found, creating new database")
            leads_data = []
        
        # Find and update the lead
        lead_found = False
        current_time = json.loads(json.dumps({"timestamp": "2024-01-15T" + str(hash(briefing) % 24).zfill(2) + ":00:00Z"}))["timestamp"]
        
        for lead in leads_data:
            if lead.get('lead_id') == lead_id:
                lead['ai_briefing'] = briefing
                lead['last_updated'] = current_time
                lead['status'] = 'Briefing Generated'
                lead_found = True
                print(f"✅ Updated existing lead: {lead.get('name', 'Unknown')} ({lead_id})")
                break
        
        # If lead not found, create a new entry
        if not lead_found:
            new_lead = {
                "lead_id": lead_id,
                "name": "Unknown Lead",
                "company": "Unknown Company", 
                "email": "unknown@example.com",
                "status": "Briefing Generated",
                "ai_briefing": briefing,
                "created_date": current_time,
                "last_updated": current_time
            }
            leads_data.append(new_lead)
            print(f"✅ Created new lead entry: {lead_id}")
        
        # Save updated database
        with open('leads_db.json', 'w') as file:
            json.dump(leads_data, file, indent=2)
        
        print(f"📄 Briefing saved to local database")
        print(f"📊 Database now contains {len(leads_data)} leads")
        print("--- END LOCAL DATABASE UPDATE ---")
        
    except Exception as e:
        print(f"--- DATABASE UPDATE ERROR ---")
        print(f"Failed to update Lead ID: {lead_id}")
        print(f"Error: {str(e)}")
        print("--- END DATABASE UPDATE ERROR ---")


# FastAPI webhook endpoint
@app.post("/webhook")
async def webhook_endpoint(request: WebhookRequest):
    """
    Webhook endpoint that receives lead information and generates AI briefing
    """
    try:
        print(f">>> Processing webhook for Lead ID: {request.lead_id} <<<")
        
        # 1. Get company intelligence
        general_info = get_company_intelligence(request.company_domain)
        
        # 2. Get lead-specific context
        specific_info = get_lead_context(request.context_id)
        
        if general_info and specific_info:
            # 3. Generate AI briefing
            specific_context_str = json.dumps(specific_info)
            briefing_json = generate_ai_briefing(general_info, specific_context_str)
            
            # 4. Update Salesforce with the briefing
            if briefing_json:
                update_salesforce(request.lead_id, briefing_json)
                
                return {
                    "status": "success",
                    "message": f"Successfully generated and updated briefing for lead {request.lead_id}",
                    "briefing": json.loads(briefing_json)
                }
            else:
                return {
                    "status": "error", 
                    "message": "Failed to generate AI briefing"
                }
        else:
            return {
                "status": "error",
                "message": "Failed to gather company intelligence or lead context"
            }
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Pre-Call Briefing Assistant"}

# View leads database endpoint
@app.get("/leads")
async def get_leads():
    """View all leads in the local database"""
    try:
        with open('leads_db.json', 'r') as file:
            leads_data = json.load(file)
        
        return {
            "total_leads": len(leads_data),
            "leads": leads_data
        }
    except FileNotFoundError:
        return {
            "total_leads": 0,
            "leads": [],
            "message": "No leads database found"
        }
    except Exception as e:
        return {
            "error": f"Failed to read leads database: {str(e)}"
        }

# For local testing, keep the original test code but make it optional
if __name__ == "__main__":
    print(">>> Running Local Test <<<")

    # 1. Hardcode test data
    TEST_DOMAIN = "hubspot.com"  # Use a real domain for better results
    TEST_CONTEXT_ID = "ad_001_pos"
    TEST_LEAD_ID = "00Qabc00001defGHI" # A dummy Salesforce Lead ID

    # 2. Call your functions in order
    general_info = get_company_intelligence(TEST_DOMAIN)
    specific_info = get_lead_context(TEST_CONTEXT_ID)

    if general_info and specific_info:
        specific_context_str = json.dumps(specific_info)
        briefing_json = generate_ai_briefing(general_info, specific_context_str)

        # 3. Call the dummy Salesforce update function
        if briefing_json:
            update_salesforce(TEST_LEAD_ID, briefing_json)

    print(">>> Local Test Complete <<<") 