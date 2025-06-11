# AI Pre-Call Briefing Assistant

An AI-powered sales briefing assistant that automatically generates comprehensive pre-call briefings for sales representatives by combining company intelligence with lead-specific context.

## Features

- **Company Intelligence Gathering**: Scrapes company websites and fetches recent news
- **Lead Context Integration**: Pulls lead-specific context from ad campaigns and marketing materials  
- **AI-Powered Briefing Generation**: Uses Groq's LLaMA model to generate structured JSON briefings
- **Salesforce Integration**: Automatically updates lead records with generated briefings
- **FastAPI Webhook**: RESTful API endpoint for integration with CRM systems

## Project Structure

```
├── main.py              # Main application with FastAPI endpoints and core logic
├── config.py            # Configuration management for API keys and credentials
├── mock_db.json         # Sample lead context database
├── .env                 # Environment variables (API keys, credentials)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual API keys:

```env
GROQ_API_KEY="your_actual_groq_api_key"
NEWS_API_KEY="your_news_api_key"
SALESFORCE_USERNAME="your.salesforce@email.com"
SALESFORCE_PASSWORD="YourSalesforcePassword"
SALESFORCE_SECURITY_TOKEN="YourSalesforceSecurityToken"
```

### 3. Test Locally

Run the standalone test:
```bash
python main.py
```

Start the web server:
```bash
uvicorn main:app --reload
```

Test the webhook:
```bash
curl -X POST "http://127.0.0.1:8000/webhook" \
  -H "Content-Type: application/json" \
  -d '{"company_domain": "hubspot.com", "context_id": "ad_001_pos", "lead_id": "00Qabc00001defGHI"}'
```

## API Endpoints

### POST /webhook
Main webhook endpoint that processes lead briefing requests.

**Request Body:**
```json
{
  "company_domain": "example.com",
  "context_id": "ad_001_pos", 
  "lead_id": "00Qabc00001defGHI"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully generated and updated briefing for lead 00Qabc00001defGHI",
  "briefing": {
    "company_profile": "...",
    "key_updates": "...",
    "lead_angle": "...",
    "conversation_starters": "...",
    "potential_objections": "..."
  }
}
```

### GET /
Health check endpoint.

## Salesforce Integration

### Custom Field Setup
1. In Salesforce Setup, go to Object Manager → Lead → Fields & Relationships
2. Create a new field:
   - Data Type: Text Area (Long)
   - Field Label: AI Pre-Call Briefing
   - Field Name: AI_Pre_Call_Briefing__c

### Webhook Integration
Set up Flow or Outbound Messages in Salesforce to call the webhook when leads are created/updated.

## Deployment

The application is ready for deployment to cloud platforms like:
- Google Cloud Functions
- AWS Lambda
- Heroku
- DigitalOcean App Platform

Make sure to set environment variables in your deployment platform.

## Error Handling

The application includes comprehensive error handling:
- Graceful fallbacks when API keys are not configured
- Mock responses for testing without real credentials
- Detailed error logging and user-friendly error messages
- Timeout handling for external API calls

## Dependencies

Key dependencies include:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `groq` - Groq API client for LLaMA model
- `requests` - HTTP client for web scraping and API calls
- `beautifulsoup4` - HTML parsing for web scraping
- `simple-salesforce` - Salesforce API integration
- `python-dotenv` - Environment variable management

## License

This project was created as part of a hackathon and is intended for educational/demonstration purposes. # StoreHubProjects-AIBriefingAssistant
# StoreHubProjects-AIBriefingAssistant2
