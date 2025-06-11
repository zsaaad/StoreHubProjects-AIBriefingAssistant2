"""
AI Pre-Call Briefing Assistant

A FastAPI application that generates AI-powered sales briefings by combining
company intelligence gathering with lead-specific context analysis.

Architecture:
- Modular service classes for different responsibilities
- Comprehensive error handling and logging
- Type safety with proper annotations
- Clean separation of concerns
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from pydantic import BaseModel, Field
from pydantic import field_validator

from config import config, ConfigurationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="AI Pre-Call Briefing Assistant",
    description="Generate AI-powered sales briefings from company intelligence and lead context",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATA MODELS ===

class WebhookRequest(BaseModel):
    """Request model for webhook endpoint with validation."""
    
    company_domain: str = Field(
        ..., 
        description="Company domain (e.g., 'example.com')",
        min_length=3,
        max_length=100
    )
    context_id: str = Field(
        ..., 
        description="Lead context identifier from marketing campaigns",
        min_length=1,
        max_length=50
    )
    lead_id: str = Field(
        ..., 
        description="Unique lead identifier",
        min_length=1,
        max_length=50
    )
    
    @field_validator('company_domain')
    @classmethod
    def validate_domain(cls, v):
        """Validate domain format."""
        # Remove protocol if present
        domain = v.lower().replace('http://', '').replace('https://', '')
        if '.' not in domain:
            raise ValueError('Invalid domain format')
        return domain

@dataclass
class BriefingData:
    """Structured data container for briefing information."""
    company_profile: str
    key_updates: List[str]
    lead_angle: str
    conversation_starters: List[str]
    potential_objections: List[str]
    error: Optional[str] = None

class CompanyIntelligence:
    """Container for company intelligence data."""
    
    def __init__(self, homepage_content: str, news_headlines: List[str], error: Optional[str] = None):
        self.homepage_content = homepage_content
        self.news_headlines = news_headlines
        self.error = error
    
    @property
    def is_valid(self) -> bool:
        """Check if intelligence data is valid and usable."""
        return self.error is None and len(self.homepage_content.strip()) > 0

# === SERVICE CLASSES ===

class WebScrapingService:
    """Handles web scraping and content extraction with robust error handling."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def scrape_company_website(self, domain: str, max_chars: int = 2000) -> Tuple[str, Optional[str]]:
        """
        Scrape company website content with comprehensive error handling.
        
        Args:
            domain: Company domain to scrape
            max_chars: Maximum characters to extract from content
            
        Returns:
            Tuple of (content, error_message)
        """
        try:
            # Construct URL with proper protocol
            url = f"https://{domain}" if not domain.startswith('http') else domain
            
            logger.info(f"Scraping website: {url}")
            
            # Make request with timeout and error handling
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements for clean text
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()
            
            # Extract and clean text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            content = cleaned_text[:max_chars]
            
            logger.info(f"Successfully scraped {len(content)} characters from {domain}")
            return content, None
            
        except requests.RequestException as e:
            error_msg = f"Failed to access website {domain}: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error scraping {domain}: {str(e)}"
            logger.error(error_msg)
            return "", error_msg

class NewsService:
    """Handles news API integration for company updates."""
    
    async def fetch_company_news(self, company_name: str, max_articles: int = 3) -> Tuple[List[str], Optional[str]]:
        """
        Fetch recent news headlines for a company.
        
        Args:
            company_name: Company name to search for
            max_articles: Maximum number of articles to fetch
            
        Returns:
            Tuple of (headlines_list, error_message)
        """
        if not config.is_news_api_configured:
            logger.warning("News API not configured, using fallback")
            return ["News API not configured - add NEWS_API_KEY to .env"], None
        
        try:
            news_url = (
                f"https://newsapi.org/v2/everything?"
                f"q={company_name}&"
                f"apiKey={config.news_api_key}&"
                f"pageSize={max_articles}&"
                f"sortBy=publishedAt"
            )
            
            logger.info(f"Fetching news for: {company_name}")
            
            response = requests.get(news_url, timeout=10)
            response.raise_for_status()
            
            news_data = response.json()
            
            headlines = []
            for article in news_data.get('articles', []):
                if article.get('title'):
                    headlines.append(article['title'])
            
            if not headlines:
                headlines = [f"No recent news found for {company_name}"]
            
            logger.info(f"Found {len(headlines)} news articles")
            return headlines, None
            
        except requests.RequestException as e:
            error_msg = f"Failed to fetch news: {str(e)}"
            logger.error(error_msg)
            return [f"Error fetching news: {str(e)}"], error_msg
        except Exception as e:
            error_msg = f"Unexpected error in news service: {str(e)}"
            logger.error(error_msg)
            return [f"News service error: {str(e)}"], error_msg

class IntelligenceService:
    """Orchestrates company intelligence gathering from multiple sources."""
    
    def __init__(self):
        self.web_scraper = WebScrapingService()
        self.news_service = NewsService()
    
    async def gather_company_intelligence(self, domain: str) -> CompanyIntelligence:
        """
        Gather comprehensive company intelligence from website and news sources.
        
        Args:
            domain: Company domain to investigate
            
        Returns:
            CompanyIntelligence object with gathered data
        """
        try:
            # Extract company name from domain for news search
            company_name = domain.split('.')[0].replace('-', ' ').title()
            
            # Gather data concurrently for better performance
            website_task = self.web_scraper.scrape_company_website(domain)
            news_task = self.news_service.fetch_company_news(company_name)
            
            # Execute both tasks concurrently
            (website_content, website_error), (news_headlines, news_error) = await asyncio.gather(
                website_task, news_task, return_exceptions=True
            )
            
            # Handle any exceptions from gather
            if isinstance(website_content, Exception):
                website_content, website_error = "", str(website_content)
            if isinstance(news_headlines, Exception):
                news_headlines, news_error = [f"News error: {str(news_headlines)}"], str(news_headlines)
            
            # Determine if there are critical errors
            error = None
            if website_error and not website_content:
                error = f"Critical error: {website_error}"
            
            return CompanyIntelligence(
                homepage_content=website_content,
                news_headlines=news_headlines,
                error=error
            )
            
        except Exception as e:
            error_msg = f"Intelligence gathering failed: {str(e)}"
            logger.error(error_msg)
            return CompanyIntelligence(
                homepage_content="",
                news_headlines=[],
                error=error_msg
            )

class LeadContextService:
    """Manages lead context retrieval and validation."""
    
    async def get_lead_context(self, context_id: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Retrieve lead context from the mock database with proper error handling.
        
        Args:
            context_id: Unique identifier for lead context
            
        Returns:
            Tuple of (context_data, error_message)
        """
        try:
            with open('mock_db.json', 'r') as file:
                data = json.load(file)
            
            for entry in data:
                if entry.get('context_id') == context_id:
                    logger.info(f"Found context for ID: {context_id}")
                    return entry, None
            
            error_msg = f"Context ID '{context_id}' not found in database"
            logger.warning(error_msg)
            return {}, error_msg
            
        except FileNotFoundError:
            error_msg = "Context database (mock_db.json) not found"
            logger.error(error_msg)
            return {}, error_msg
        except json.JSONDecodeError:
            error_msg = "Invalid JSON in context database"
            logger.error(error_msg)
            return {}, error_msg
        except Exception as e:
            error_msg = f"Error reading context database: {str(e)}"
            logger.error(error_msg)
            return {}, error_msg

class AIBriefingService:
    """Handles AI-powered briefing generation using Groq."""
    
    def __init__(self):
        self.client = None
        if config.is_groq_configured:
            self.client = Groq(api_key=config.groq_api_key)
    
    async def generate_briefing(self, intelligence: CompanyIntelligence, lead_context: Dict[str, Any]) -> BriefingData:
        """
        Generate AI-powered briefing from company intelligence and lead context.
        
        Args:
            intelligence: Gathered company intelligence
            lead_context: Lead-specific context data
            
        Returns:
            BriefingData object with generated briefing
        """
        if not config.is_groq_configured:
            logger.warning("Groq API not configured")
            return BriefingData(
                company_profile="Groq API key required - add to .env file",
                key_updates=["API configuration needed"],
                lead_angle="Configure Groq API for AI briefings",
                conversation_starters=["Set up API keys for full functionality"],
                potential_objections=[{"objection": "API not configured", "response": "Configure Groq API key"}],
                error="Groq API not configured"
            )
        
        try:
            # Construct system prompt with clear instructions
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(intelligence, lead_context)
            
            logger.info("Generating AI briefing...")
            
            # Call Groq API with retry logic
            for attempt in range(2):  # Two attempts
                try:
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        model="llama3-8b-8192",
                        response_format={"type": "json_object"},
                        temperature=0.5,  # Lower temperature for more consistent JSON
                        max_tokens=1200
                    )
                    
                    # Parse and validate response
                    response_content = chat_completion.choices[0].message.content
                    logger.info(f"Raw AI response: {response_content[:200]}...")
                    
                    briefing_json = json.loads(response_content)
                    
                    # Validate required keys and structure
                    required_keys = ['company_profile', 'key_updates', 'lead_angle', 'conversation_starters', 'potential_objections']
                    for key in required_keys:
                        if key not in briefing_json:
                            raise ValueError(f"Missing required key: {key}")
                    
                    # Ensure proper data types
                    if not isinstance(briefing_json.get('key_updates'), list):
                        briefing_json['key_updates'] = [str(briefing_json.get('key_updates', ''))]
                    
                    if not isinstance(briefing_json.get('conversation_starters'), list):
                        briefing_json['conversation_starters'] = [str(briefing_json.get('conversation_starters', ''))]
                    
                    if not isinstance(briefing_json.get('potential_objections'), list):
                        objections = briefing_json.get('potential_objections', [])
                        if isinstance(objections, str):
                            briefing_json['potential_objections'] = [{"objection": objections, "response": "Address this concern"}]
                        elif isinstance(objections, list) and objections:
                            # Ensure each objection is properly structured
                            formatted_objections = []
                            for obj in objections:
                                if isinstance(obj, dict) and 'objection' in obj:
                                    formatted_objections.append(obj)
                                else:
                                    formatted_objections.append({"objection": str(obj), "response": "Address this concern"})
                            briefing_json['potential_objections'] = formatted_objections
                    
                    logger.info("Successfully generated AI briefing")
                    
                    return BriefingData(
                        company_profile=briefing_json.get('company_profile', 'Company analysis available'),
                        key_updates=briefing_json.get('key_updates', ['Recent updates identified']),
                        lead_angle=briefing_json.get('lead_angle', 'Customized approach recommended'),
                        conversation_starters=briefing_json.get('conversation_starters', ['Key questions prepared']),
                        potential_objections=briefing_json.get('potential_objections', [{"objection": "Common concerns", "response": "Address professionally"}])
                    )
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed on attempt {attempt + 1}: {str(e)}")
                    if attempt == 1:  # Last attempt
                        raise e
                    continue
                    
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from AI after retries: {str(e)}"
            logger.error(error_msg)
            return self._create_error_briefing(error_msg)
        except Exception as e:
            error_msg = f"AI briefing generation failed: {str(e)}"
            logger.error(error_msg)
            return self._create_error_briefing(error_msg)
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for AI briefing generation."""
        return """You are an expert B2B sales intelligence assistant. Generate comprehensive pre-call briefings that help sales representatives prepare for prospect conversations.

        CRITICAL: Your response MUST be valid JSON format only. Do not include any markdown, explanations, or text outside the JSON structure.

        Required JSON structure:
        {
            "company_profile": "String - Concise business overview, industry, and key characteristics",
            "key_updates": ["Array of strings - Recent developments, news, or changes"],
            "lead_angle": "String - Specific value proposition based on lead context",
            "conversation_starters": [
                "String - Question 1",
                "String - Question 2", 
                "String - Question 3"
            ],
            "potential_objections": [
                {
                    "objection": "String - Common objection",
                    "response": "String - How to handle it"
                }
            ]
        }

        Focus on actionable insights that enable more effective prospect conversations.
        Be specific, professional, and sales-oriented in your analysis.
        Ensure all JSON strings are properly escaped and the response is valid JSON."""
    
    def _build_user_prompt(self, intelligence: CompanyIntelligence, lead_context: Dict[str, Any]) -> str:
        """Build user prompt with context data."""
        news_text = "\n".join(f"- {headline}" for headline in intelligence.news_headlines)
        context_text = json.dumps(lead_context, indent=2)
        
        return f"""Generate a pre-call briefing based on this information:

        COMPANY WEBSITE CONTENT:
        {intelligence.homepage_content}

        RECENT NEWS & UPDATES:
        {news_text}

        LEAD CONTEXT & CAMPAIGN DATA:
        {context_text}

        Provide a comprehensive JSON briefing for the sales representative."""
    
    def _create_error_briefing(self, error_msg: str) -> BriefingData:
        """Create fallback briefing for error scenarios."""
        return BriefingData(
            company_profile=f"Unable to generate full briefing due to technical issues. Manual research recommended for this lead.",
            key_updates=["Briefing generation encountered technical difficulties", "Manual lead research advised"],
            lead_angle="Proceed with standard qualification approach while technical issues are resolved",
            conversation_starters=[
                "Tell me about your current business challenges",
                "What solutions are you currently evaluating?", 
                "What's your timeline for implementing new solutions?"
            ],
            potential_objections=[
                {"objection": "Not interested in demos right now", "response": "I understand timing is important. Can we schedule a brief 10-minute call to understand your needs better?"},
                {"objection": "We're happy with our current solution", "response": "That's great to hear. I'd love to learn what's working well and see if we can add additional value."}
            ],
            error=error_msg
        )

class DatabaseService:
    """Manages local database operations for lead tracking."""
    
    async def update_lead_with_briefing(self, lead_id: str, briefing_data: BriefingData) -> bool:
        """
        Update lead record with generated briefing.
        
        Args:
            lead_id: Unique lead identifier
            briefing_data: Generated briefing data
            
        Returns:
            Success status
        """
        if config.is_salesforce_configured:
            return await self._update_salesforce_lead(lead_id, briefing_data)
        else:
            return await self._update_local_database(lead_id, briefing_data)
    
    async def _update_salesforce_lead(self, lead_id: str, briefing_data: BriefingData) -> bool:
        """Update Salesforce lead record."""
        try:
            from simple_salesforce import Salesforce
            
            sf = Salesforce(
                username=config.salesforce_username,
                password=config.salesforce_password,
                security_token=config.salesforce_security_token
            )
            
            briefing_json = json.dumps({
                "company_profile": briefing_data.company_profile,
                "key_updates": briefing_data.key_updates,
                "lead_angle": briefing_data.lead_angle,
                "conversation_starters": briefing_data.conversation_starters,
                "potential_objections": briefing_data.potential_objections
            })
            
            sf.Lead.update(lead_id, {'AI_Pre_Call_Briefing__c': briefing_json})
            
            logger.info(f"✅ Updated Salesforce lead: {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Salesforce update failed: {str(e)}")
            return False
    
    async def _update_local_database(self, lead_id: str, briefing_data: BriefingData) -> bool:
        """Update local JSON database."""
        try:
            # Read existing data
            try:
                with open('leads_db.json', 'r') as file:
                    leads_data = json.load(file)
            except FileNotFoundError:
                leads_data = []
            
            # Prepare briefing JSON
            briefing_json = json.dumps({
                "company_profile": briefing_data.company_profile,
                "key_updates": briefing_data.key_updates,
                "lead_angle": briefing_data.lead_angle,
                "conversation_starters": briefing_data.conversation_starters,
                "potential_objections": briefing_data.potential_objections
            })
            
            # Update or create lead record
            current_time = datetime.now().isoformat()
            lead_found = False
            
            for lead in leads_data:
                if lead.get('lead_id') == lead_id:
                    lead['ai_briefing'] = briefing_json
                    lead['last_updated'] = current_time
                    lead['status'] = 'Briefing Generated'
                    lead_found = True
                    logger.info(f"✅ Updated existing lead: {lead.get('name', 'Unknown')} ({lead_id})")
                    break
            
            if not lead_found:
                new_lead = {
                    "lead_id": lead_id,
                    "name": "Unknown Lead",
                    "company": "Unknown Company",
                    "email": "unknown@example.com",
                    "status": "Briefing Generated",
                    "ai_briefing": briefing_json,
                    "created_date": current_time,
                    "last_updated": current_time
                }
                leads_data.append(new_lead)
                logger.info(f"✅ Created new lead entry: {lead_id}")
            
            # Save updated database
            with open('leads_db.json', 'w') as file:
                json.dump(leads_data, file, indent=2)
            
            logger.info(f"📄 Database updated successfully ({len(leads_data)} total leads)")
            return True
            
        except Exception as e:
            logger.error(f"Database update failed: {str(e)}")
            return False

# === SERVICE INSTANCES ===

intelligence_service = IntelligenceService()
lead_context_service = LeadContextService()
ai_briefing_service = AIBriefingService()
database_service = DatabaseService()

# === API ENDPOINTS ===

@app.post("/webhook", summary="Generate AI Briefing", response_description="Briefing generation result")
async def generate_briefing_webhook(request: WebhookRequest):
    """
    Generate AI-powered pre-call briefing for a sales lead.
    
    This endpoint orchestrates the entire briefing generation process:
    1. Gathers company intelligence from website and news sources
    2. Retrieves lead-specific context from campaign data
    3. Generates AI briefing using Groq LLM
    4. Updates lead record in database (Salesforce or local)
    
    Args:
        request: Webhook request containing company domain, context ID, and lead ID
        
    Returns:
        JSON response with briefing data and processing status
    """
    start_time = datetime.now()
    logger.info(f"🚀 Processing briefing request for lead: {request.lead_id}")
    
    try:
        # Step 1: Gather company intelligence
        intelligence = await intelligence_service.gather_company_intelligence(request.company_domain)
        
        if not intelligence.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to gather company intelligence: {intelligence.error}"
            )
        
        # Step 2: Get lead context
        lead_context, context_error = await lead_context_service.get_lead_context(request.context_id)
        
        if context_error:
            logger.warning(f"Context retrieval warning: {context_error}")
            # Continue with empty context rather than failing
        
        # Step 3: Generate AI briefing
        briefing = await ai_briefing_service.generate_briefing(intelligence, lead_context)
        
        # Step 4: Update database
        update_success = await database_service.update_lead_with_briefing(request.lead_id, briefing)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Briefing generated successfully in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "message": f"Successfully generated briefing for lead {request.lead_id}",
            "briefing": {
                "company_profile": briefing.company_profile,
                "key_updates": briefing.key_updates,
                "lead_angle": briefing.lead_angle,
                "conversation_starters": briefing.conversation_starters,
                "potential_objections": briefing.potential_objections
            },
            "metadata": {
                "processing_time_seconds": processing_time,
                "database_updated": update_success,
                "context_found": context_error is None,
                "intelligence_valid": intelligence.is_valid
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Briefing generation failed: {str(e)}")
        
        # Return a structured error response with fallback briefing
        error_briefing = ai_briefing_service._create_error_briefing(str(e))
        
        return {
            "status": "error",
            "message": f"Briefing generation encountered issues for lead {request.lead_id}",
            "briefing": {
                "company_profile": error_briefing.company_profile,
                "key_updates": error_briefing.key_updates,
                "lead_angle": error_briefing.lead_angle,
                "conversation_starters": error_briefing.conversation_starters,
                "potential_objections": error_briefing.potential_objections
            },
            "metadata": {
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "database_updated": False,
                "context_found": False,
                "intelligence_valid": False,
                "error": str(e)
            }
        }

@app.get("/", summary="Health Check")
async def health_check():
    """Health check endpoint with system status."""
    return {
        "status": "healthy",
        "service": "AI Pre-Call Briefing Assistant",
        "version": "1.0.0",
        "configuration": {
            "groq_configured": config.is_groq_configured,
            "news_api_configured": config.is_news_api_configured,
            "salesforce_configured": config.is_salesforce_configured
        }
    }

@app.get("/leads", summary="View Leads Database")
async def get_leads():
    """View all leads in the local database with briefing status."""
    try:
        with open('leads_db.json', 'r') as file:
            leads_data = json.load(file)
        
        # Add briefing status to each lead
        for lead in leads_data:
            lead['has_briefing'] = bool(lead.get('ai_briefing'))
        
        return {
            "total_leads": len(leads_data),
            "leads_with_briefings": sum(1 for lead in leads_data if lead.get('has_briefing')),
            "leads": leads_data
        }
    except FileNotFoundError:
        return {
            "total_leads": 0,
            "leads_with_briefings": 0,
            "leads": [],
            "message": "No leads database found"
        }
    except Exception as e:
        logger.error(f"Error reading leads database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read leads database: {str(e)}"
        )

@app.get("/config", summary="Configuration Status")
async def get_configuration_status():
    """Get current configuration status for troubleshooting."""
    return {
        "services": {
            "groq_api": {
                "configured": config.is_groq_configured,
                "status": "✅ Ready" if config.is_groq_configured else "⚠️ Not configured"
            },
            "news_api": {
                "configured": config.is_news_api_configured,
                "status": "✅ Ready" if config.is_news_api_configured else "⚠️ Not configured"
            },
            "salesforce": {
                "configured": config.is_salesforce_configured,
                "status": "✅ Ready" if config.is_salesforce_configured else "⚠️ Using local database"
            }
        },
        "recommendations": [
            "Add GROQ_API_KEY to .env for AI briefing generation" if not config.is_groq_configured else None,
            "Add NEWS_API_KEY to .env for company news integration" if not config.is_news_api_configured else None,
            "Configure Salesforce credentials for CRM integration" if not config.is_salesforce_configured else None
        ]
    }

# === FRONTEND ENDPOINTS ===

@app.get("/app", response_class=HTMLResponse, summary="Web Application")
async def get_web_app():
    """Serve the web application interface."""
    try:
        with open("templates/index.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Web app not found</h1><p>Frontend template missing.</p>", status_code=404)

@app.get("/api/generic-script", summary="Get Generic Sales Script")
async def get_generic_script():
    """Return a generic sales script for comparison."""
    generic_script = """Hi [Contact Name], this is [Your Name] from [Company Name].

I hope you're having a great day! I'm calling because we provide comprehensive technology solutions that help businesses improve their operations and reduce costs.

Our platform offers a wide range of features including:
- Advanced analytics and reporting
- Cloud-based infrastructure
- 24/7 customer support
- Enterprise-grade security
- Scalable architecture

We've helped thousands of companies across various industries achieve significant cost savings and operational improvements.

I'd love to schedule a quick 15-minute call to show you our solutions and discuss how we can help your business. We're currently offering a special promotion for new customers.

Are you available this week for a brief demo? I have some time Tuesday or Wednesday that could work.

What do you think? Can we set something up?"""

    return {"script": generic_script}

@app.get("/api/mock-lead", summary="Get Mock Lead Data")
async def get_mock_lead():
    """Return mock lead data using the rich CSV dataset structure."""
    # Import the new mock leads data
    from mock_leads_data import get_all_leads, get_lead_context, BUSINESS_INTELLIGENCE
    
    # Get a random lead from the CSV data
    import random
    all_leads = get_all_leads()
    selected_lead = random.choice(all_leads)
    
    # Get enhanced context for this lead
    lead_context = get_lead_context(selected_lead["lead_id"])
    business_intel = BUSINESS_INTELLIGENCE.get(selected_lead["company_name"], {})
    
    # Convert to frontend format with enhanced structure
    mock_lead = {
        "lead_id": selected_lead["lead_id"],
        "contact": {
            "name": selected_lead.get("lead_name", ""),
            "first_name": selected_lead.get("lead_name", "").split()[0] if selected_lead.get("lead_name") else "",
            "title": selected_lead.get("contact_role", ""),
            "email": selected_lead.get("email", ""),
            "phone": selected_lead.get("phone", ""),
            "preferred_language": selected_lead.get("preferred_language", "English")
        },
        "company": {
            "name": selected_lead["company_name"],
            "store_name": selected_lead.get("business_store_name", ""),
            "industry": selected_lead.get("industry", ""),
            "sub_industry": selected_lead.get("sub_industry", ""),
            "business_operation": selected_lead.get("business_operation", ""),
            "website": selected_lead["company_domain"],
            "pain_points": business_intel.get("pain_points", []),
            "revenue_profile": {
                "monthly_revenue": f"RM{selected_lead.get('average_revenue_month', 0):,}",
                "daily_orders": selected_lead.get("average_orders_per_day", 0),
                "basket_size": f"RM{selected_lead.get('basket_size_order', 0)}",
                "revenue_segment": business_intel.get("revenue_segment", "Unknown")
            },
            "operational_details": {
                "outlets": selected_lead.get("num_outlets", 1),
                "current_platform": selected_lead.get("merchant_current_platform", "None"),
                "existing_pos": selected_lead.get("existing_pos_system", "None"),
                "urgency": selected_lead.get("when_need_pos", "Not specified")
            }
        },
        "lead_source": "Digital Advertisement",
        "campaign": lead_context["ad_context"].get("title", "StoreHub Solution") if lead_context else "StoreHub Solution",
        "interest_level": business_intel.get("urgency", "Medium"),
        "context_id": selected_lead["context_id"],
        "notes": f"Clicked on {lead_context['ad_context'].get('title', 'advertisement')} - {lead_context['ad_context'].get('focus', 'business solution')}" if lead_context else "Interested in business solutions",
        "news_snippets": [
            {
                "headline": f"{selected_lead['company_name']} Embraces Digital Transformation",
                "source": "Business Today Malaysia",
                "date": "2024-01-15",
                "snippet": f"Local {selected_lead.get('sub_industry', 'business')} {selected_lead['company_name']} joins the digital revolution to improve customer experience."
            },
            {
                "headline": f"Malaysian {selected_lead.get('industry', 'Business')} Sector Shows Strong Growth",
                "source": "The Edge Malaysia",
                "date": "2024-01-12", 
                "snippet": f"{selected_lead.get('industry', 'Business')} businesses are increasingly adopting technology solutions to stay competitive."
            },
            {
                "headline": "Small Business Tech Adoption Accelerates Post-Pandemic",
                "source": "The Star",
                "date": "2024-01-10",
                "snippet": "Malaysian SMEs are rapidly digitalizing operations to meet changing consumer expectations."
            }
        ],
        "page_visited": {
            "url": selected_lead["source_visual_url"],
            "title": lead_context["ad_context"].get("title", "StoreHub Solutions") if lead_context else "StoreHub Solutions",
            "time_spent": "3 minutes 45 seconds",
            "sections_viewed": ["Features", "Pricing", "Case Studies"],
            "preview": lead_context["ad_context"].get("solution_angle", "Complete business solution") if lead_context else "Complete business solution for modern businesses"
        },
        "ad_creative": {
            "campaign": lead_context["ad_context"].get("title", "StoreHub Solutions") if lead_context else "StoreHub Solutions",
            "headline": f"Perfect Solution for {selected_lead.get('sub_industry', 'Your Business')}",
            "description": f"Trusted by {selected_lead.get('industry', 'business')} owners across Malaysia. Increase efficiency and grow your revenue.",
            "cta": "Get Free Demo",
            "image_description": lead_context["ad_context"].get("title", "Business solution") if lead_context else "Modern business solution interface",
            "targeting": f"{selected_lead.get('contact_role', 'Business Owner')}s in {selected_lead.get('industry', 'Business')} industry, Malaysia"
        }
    }
    
    return mock_lead

# === DEVELOPMENT & TESTING ===

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting AI Pre-Call Briefing Assistant in development mode")
    
    # Run local test if requested
    if "--test" in __import__("sys").argv:
        async def run_test():
            """Run comprehensive local test."""
            print("\n🧪 Running comprehensive test...")
            
            test_request = WebhookRequest(
                company_domain="hubspot.com",
                context_id="ad_001_pos", 
                lead_id="test_lead_001"
            )
            
            try:
                result = await generate_briefing_webhook(test_request)
                print("✅ Test completed successfully!")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
        
        asyncio.run(run_test())
    else:
        # Start development server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        ) 