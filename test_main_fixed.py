"""
Comprehensive unit tests for AI Pre-Call Briefing Assistant - Fixed Version.

Tests cover all major functionality with proper mocking techniques.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient

from main import (
    app, WebScrapingService, NewsService, IntelligenceService,
    LeadContextService, AIBriefingService, DatabaseService,
    BriefingData, CompanyIntelligence, WebhookRequest
)

# Test client for FastAPI endpoints
client = TestClient(app)

# === FIXTURES ===

@pytest.fixture
def mock_website_response():
    """Mock successful website response."""
    return """
    <html>
        <head><title>Test Company</title></head>
        <body>
            <h1>Welcome to Test Company</h1>
            <p>We provide innovative business solutions for modern enterprises.</p>
            <p>Our services include consulting, software development, and support.</p>
        </body>
    </html>
    """

@pytest.fixture
def mock_news_response():
    """Mock successful news API response."""
    return {
        "articles": [
            {"title": "Test Company Announces New Product Launch"},
            {"title": "Test Company Raises $50M in Series B Funding"},
            {"title": "Test Company Expands to European Markets"}
        ]
    }

@pytest.fixture
def mock_lead_context():
    """Mock lead context data."""
    return {
        "context_id": "ad_001_pos",
        "source_copy": "Transform your business with our cloud-based POS system",
        "landing_page_url": "https://example.com/pos-solution"
    }

@pytest.fixture
def mock_briefing_data():
    """Mock AI-generated briefing data."""
    return BriefingData(
        company_profile="Test Company is a leading provider of business solutions",
        key_updates=["New product launch", "Series B funding", "European expansion"],
        lead_angle="Focus on cloud-based POS system benefits",
        conversation_starters=[
            "How are you currently handling point-of-sale operations?",
            "What challenges do you face with your current POS system?"
        ],
        potential_objections=["Cost concerns", "Integration complexity"]
    )

# === WEB SCRAPING SERVICE TESTS ===

class TestWebScrapingService:
    """Test cases for WebScrapingService."""
    
    @pytest.mark.asyncio
    async def test_scrape_company_website_success(self, mock_website_response):
        """Test successful website scraping."""
        service = WebScrapingService()
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.content = mock_website_response.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            content, error = await service.scrape_company_website("example.com")
            
            assert error is None
            assert "Test Company" in content
            assert "business solutions" in content
            assert len(content) <= 2000  # Respects max_chars limit
    
    @pytest.mark.asyncio
    async def test_scrape_company_website_request_error(self):
        """Test website scraping with request error."""
        service = WebScrapingService()
        
        with patch('requests.Session.get', side_effect=Exception("Connection failed")):
            content, error = await service.scrape_company_website("invalid-domain.com")
            
            assert content == ""
            assert "Connection failed" in error

class TestNewsService:
    """Test cases for NewsService."""
    
    @pytest.mark.asyncio  
    async def test_fetch_company_news_success(self, mock_news_response):
        """Test successful news fetching."""
        service = NewsService()
        
        # Create a mock config object with proper attributes
        mock_config = Mock()
        mock_config.is_news_api_configured = True
        mock_config.news_api_key = 'test-api-key'
        
        with patch('main.config', mock_config), \
             patch('requests.get') as mock_get:
            
            mock_response = Mock()
            mock_response.json.return_value = mock_news_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            headlines, error = await service.fetch_company_news("Test Company")
            
            assert error is None
            assert len(headlines) == 3
            assert "New Product Launch" in headlines[0]
    
    @pytest.mark.asyncio
    async def test_fetch_company_news_not_configured(self):
        """Test news fetching when API is not configured."""
        service = NewsService()
        
        mock_config = Mock()
        mock_config.is_news_api_configured = False
        
        with patch('main.config', mock_config):
            headlines, error = await service.fetch_company_news("Test Company")
            
            assert error is None
            assert "not configured" in headlines[0]

class TestIntelligenceService:
    """Test cases for IntelligenceService."""
    
    @pytest.mark.asyncio
    async def test_gather_company_intelligence_success(self):
        """Test successful intelligence gathering."""
        service = IntelligenceService()
        
        with patch.object(service.web_scraper, 'scrape_company_website') as mock_scrape, \
             patch.object(service.news_service, 'fetch_company_news') as mock_news:
            
            mock_scrape.return_value = ("Website content", None)
            mock_news.return_value = (["News headline 1", "News headline 2"], None)
            
            intelligence = await service.gather_company_intelligence("example.com")
            
            assert intelligence.is_valid
            assert intelligence.homepage_content == "Website content"
            assert len(intelligence.news_headlines) == 2
            assert intelligence.error is None

class TestLeadContextService:
    """Test cases for LeadContextService."""
    
    @pytest.mark.asyncio
    async def test_get_lead_context_success(self, mock_lead_context):
        """Test successful lead context retrieval."""
        service = LeadContextService()
        
        mock_db_content = json.dumps([mock_lead_context])
        
        with patch('builtins.open', mock_open(read_data=mock_db_content)):
            context, error = await service.get_lead_context("ad_001_pos")
            
            assert error is None
            assert context["context_id"] == "ad_001_pos"
            assert "POS system" in context["source_copy"]
    
    @pytest.mark.asyncio
    async def test_get_lead_context_file_not_found(self):
        """Test lead context with missing database file."""
        service = LeadContextService()
        
        with patch('builtins.open', side_effect=FileNotFoundError()):
            context, error = await service.get_lead_context("ad_001_pos")
            
            assert "not found" in error
            assert context == {}

class TestAIBriefingService:
    """Test cases for AIBriefingService."""
    
    @pytest.mark.asyncio
    async def test_generate_briefing_success(self, mock_lead_context):
        """Test successful AI briefing generation."""
        # Create service with mocked config
        mock_config = Mock()
        mock_config.is_groq_configured = True
        mock_config.groq_api_key = 'test-key'
        
        mock_ai_response = {
            "company_profile": "Test company profile",
            "key_updates": ["Update 1", "Update 2"],
            "lead_angle": "Focus on efficiency",
            "conversation_starters": ["Question 1", "Question 2"],
            "potential_objections": ["Objection 1", "Objection 2"]
        }
        
        with patch('main.config', mock_config):
            service = AIBriefingService()
            mock_client = Mock()
            mock_completion = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = json.dumps(mock_ai_response)
            mock_choice.message = mock_message
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            service.client = mock_client
            
            intelligence = CompanyIntelligence("Test content", ["News 1", "News 2"])
            briefing = await service.generate_briefing(intelligence, mock_lead_context)
            
            assert briefing.error is None
            assert briefing.company_profile == "Test company profile"
            assert len(briefing.key_updates) == 2
    
    @pytest.mark.asyncio
    async def test_generate_briefing_not_configured(self, mock_lead_context):
        """Test AI briefing generation when Groq is not configured."""
        mock_config = Mock()
        mock_config.is_groq_configured = False
        
        with patch('main.config', mock_config):
            service = AIBriefingService()
            intelligence = CompanyIntelligence("Test content", ["News 1"])
            
            briefing = await service.generate_briefing(intelligence, mock_lead_context)
            
            assert briefing.error == "Groq API not configured"
            assert "API key required" in briefing.company_profile

class TestDatabaseService:
    """Test cases for DatabaseService."""
    
    @pytest.mark.asyncio
    async def test_update_local_database_new_lead(self, mock_briefing_data):
        """Test updating local database with new lead."""
        mock_config = Mock()
        mock_config.is_salesforce_configured = False
        
        with patch('main.config', mock_config), \
             patch('builtins.open', mock_open(read_data="[]")), \
             patch('json.dump') as mock_dump:
            
            service = DatabaseService()
            success = await service.update_lead_with_briefing("new_lead_001", mock_briefing_data)
            
            assert success
            mock_dump.assert_called_once()

# === API ENDPOINT TESTS ===

class TestAPIEndpoints:
    """Test cases for FastAPI endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI Pre-Call Briefing Assistant"
    
    def test_get_leads_empty_database(self):
        """Test get leads endpoint with empty database."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            response = client.get("/leads")
            assert response.status_code == 200
            
            data = response.json()
            assert data["total_leads"] == 0
            assert data["leads"] == []
    
    def test_get_configuration_status(self):
        """Test configuration status endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "groq_api" in data["services"]
    
    def test_webhook_endpoint_validation_error(self):
        """Test webhook endpoint with validation error."""
        invalid_request = {
            "company_domain": "",  # Too short
            "context_id": "test",
            "lead_id": "test"
        }
        
        response = client.post("/webhook", json=invalid_request)
        assert response.status_code == 422  # Validation error

# === INTEGRATION TESTS ===

class TestIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.mark.asyncio
    async def test_simplified_workflow(self, mock_lead_context):
        """Test a simplified workflow to verify core functionality."""
        
        # Test individual service components
        web_service = WebScrapingService()
        news_service = NewsService()
        context_service = LeadContextService()
        
        # Mock external calls
        with patch('requests.Session.get') as mock_web_get, \
             patch('builtins.open', mock_open(read_data=json.dumps([mock_lead_context]))):
            
            mock_response = Mock()
            mock_response.content = b"<html><body>Test content</body></html>"
            mock_response.raise_for_status.return_value = None
            mock_web_get.return_value = mock_response
            
            # Test web scraping
            content, error = await web_service.scrape_company_website("example.com")
            assert error is None
            assert "Test content" in content
            
            # Test context retrieval
            context, error = await context_service.get_lead_context("ad_001_pos")
            assert error is None
            assert context["context_id"] == "ad_001_pos"

# === PERFORMANCE TESTS ===

class TestPerformance:
    """Performance and concurrency tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test that async operations can run concurrently."""
        service = IntelligenceService()
        
        async def mock_slow_operation():
            await asyncio.sleep(0.1)
            return "result", None
        
        with patch.object(service.web_scraper, 'scrape_company_website', side_effect=mock_slow_operation), \
             patch.object(service.news_service, 'fetch_company_news', side_effect=mock_slow_operation):
            
            start_time = asyncio.get_event_loop().time()
            intelligence = await service.gather_company_intelligence("example.com")
            end_time = asyncio.get_event_loop().time()
            
            # Should take ~0.1 seconds (concurrent) rather than ~0.2 seconds (sequential)
            elapsed = end_time - start_time
            assert elapsed < 0.15, f"Expected concurrent execution (~0.1s), got {elapsed:.3f}s"

# === RUN TESTS ===

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 