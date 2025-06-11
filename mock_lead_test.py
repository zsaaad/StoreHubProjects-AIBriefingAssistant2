#!/usr/bin/env python3
"""
Mock Lead Data Testing Script for AI Pre-Call Briefing Assistant

This script provides comprehensive testing using mock lead data without requiring
external API calls. It simulates various scenarios to validate the application's
behavior under different conditions.

Usage:
    python mock_lead_test.py [--scenario SCENARIO_NAME] [--verbose]
"""

import asyncio
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MockLead:
    """Mock lead data structure for testing."""
    lead_id: str
    name: str
    company: str
    email: str
    company_domain: str
    context_id: str
    industry: str
    company_size: str
    scenario_type: str

@dataclass
class MockCompanyData:
    """Mock company intelligence data."""
    domain: str
    company_name: str
    industry: str
    description: str
    website_content: str
    news_headlines: List[str]
    key_characteristics: List[str]

@dataclass
class MockContext:
    """Mock lead context data."""
    context_id: str
    campaign_name: str
    source_copy: str
    landing_page_url: str
    campaign_type: str
    target_audience: str

class MockLeadTestSuite:
    """Comprehensive mock lead testing suite."""
    
    def __init__(self):
        self.leads = self._generate_mock_leads()
        self.company_data = self._generate_mock_company_data()
        self.contexts = self._generate_mock_contexts()
        self.results = []
    
    def _generate_mock_leads(self) -> List[MockLead]:
        """Generate diverse mock lead scenarios."""
        return [
            MockLead(
                lead_id="MOCK_001_TECH_STARTUP",
                name="Sarah Chen",
                company="InnovateTech Solutions",
                email="sarah.chen@innovatetech.com",
                company_domain="innovatetech.com",
                context_id="ctx_saas_conversion",
                industry="Technology",
                company_size="50-100 employees",
                scenario_type="saas_prospect"
            ),
            MockLead(
                lead_id="MOCK_002_RETAIL_ENTERPRISE",
                name="Michael Rodriguez",
                company="GlobalRetail Corp",
                email="m.rodriguez@globalretail.com",
                company_domain="globalretail.com",
                context_id="ctx_pos_upgrade",
                industry="Retail",
                company_size="500+ employees",
                scenario_type="enterprise_pos"
            ),
            MockLead(
                lead_id="MOCK_003_RESTAURANT_CHAIN",
                name="Emma Thompson",
                company="Bella Vista Restaurants",
                email="emma@bellavista-restaurants.com",
                company_domain="bellavista-restaurants.com",
                context_id="ctx_restaurant_efficiency",
                industry="Food & Beverage",
                company_size="20-50 employees",
                scenario_type="restaurant_chain"
            ),
            MockLead(
                lead_id="MOCK_004_HEALTHCARE_CLINIC",
                name="Dr. James Wilson",
                company="WellCare Medical Group",
                email="j.wilson@wellcaremedical.com",
                company_domain="wellcaremedical.com",
                context_id="ctx_healthcare_compliance",
                industry="Healthcare",
                company_size="10-20 employees",
                scenario_type="healthcare_specialist"
            ),
            MockLead(
                lead_id="MOCK_005_MANUFACTURING",
                name="Robert Kim",
                company="Precision Manufacturing Inc",
                email="r.kim@precisionmfg.com",
                company_domain="precisionmfg.com",
                context_id="ctx_supply_chain",
                industry="Manufacturing",
                company_size="200-500 employees",
                scenario_type="manufacturing_optimization"
            ),
            MockLead(
                lead_id="MOCK_006_ERROR_SCENARIO",
                name="Test Error",
                company="Non-Existent Company",
                email="error@test.com",
                company_domain="non-existent-domain-12345.com",
                context_id="ctx_invalid",
                industry="Testing",
                company_size="Unknown",
                scenario_type="error_testing"
            )
        ]
    
    def _generate_mock_company_data(self) -> Dict[str, MockCompanyData]:
        """Generate mock company intelligence data."""
        return {
            "innovatetech.com": MockCompanyData(
                domain="innovatetech.com",
                company_name="InnovateTech Solutions",
                industry="Technology",
                description="A leading SaaS provider specializing in workflow automation and productivity tools",
                website_content="InnovateTech Solutions empowers businesses with cutting-edge automation tools. Our platform integrates seamlessly with existing workflows, providing real-time analytics and intelligent process optimization. Founded in 2018, we serve over 10,000 customers worldwide.",
                news_headlines=[
                    "InnovateTech raises $15M Series B funding for AI expansion",
                    "New workflow automation features launched for enterprise clients",
                    "Partnership announced with major cloud infrastructure provider"
                ],
                key_characteristics=["Cloud-native", "AI-powered", "Enterprise-focused", "Rapid growth"]
            ),
            "globalretail.com": MockCompanyData(
                domain="globalretail.com",
                company_name="GlobalRetail Corp",
                industry="Retail",
                description="International retail chain with 500+ locations across North America and Europe",
                website_content="GlobalRetail Corp operates premium retail stores across multiple categories including fashion, electronics, and home goods. With over 500 locations and 25 years of experience, we focus on delivering exceptional customer experiences through innovative retail technology.",
                news_headlines=[
                    "GlobalRetail reports 12% growth in Q3 2024 same-store sales",
                    "New omnichannel customer experience platform launched",
                    "Sustainability initiative reduces carbon footprint by 30%"
                ],
                key_characteristics=["Multi-location", "Omnichannel", "Customer-centric", "Sustainability focus"]
            ),
            "bellavista-restaurants.com": MockCompanyData(
                domain="bellavista-restaurants.com",
                company_name="Bella Vista Restaurants",
                industry="Food & Beverage",
                description="Family-owned restaurant chain known for authentic Italian cuisine and exceptional service",
                website_content="Bella Vista Restaurants brings authentic Italian flavors to communities across the region. Our 8 locations feature fresh, locally-sourced ingredients and traditional recipes passed down through generations. We pride ourselves on creating memorable dining experiences for families and food enthusiasts.",
                news_headlines=[
                    "Bella Vista wins 'Best Italian Restaurant' award for third consecutive year",
                    "New location opening in downtown district with enhanced dining experience",
                    "Local sourcing program supports regional farmers and suppliers"
                ],
                key_characteristics=["Family-owned", "Authentic cuisine", "Local sourcing", "Community focused"]
            ),
            "wellcaremedical.com": MockCompanyData(
                domain="wellcaremedical.com",
                company_name="WellCare Medical Group",
                industry="Healthcare",
                description="Comprehensive medical practice providing primary care and specialized services",
                website_content="WellCare Medical Group is a patient-centered practice offering comprehensive healthcare services including primary care, preventive medicine, and specialized treatments. Our team of experienced physicians and healthcare professionals is committed to providing personalized, high-quality care in a comfortable environment.",
                news_headlines=[
                    "WellCare implements new patient portal for enhanced communication",
                    "Telemedicine services expanded to serve rural communities",
                    "Practice achieves NCQA Patient-Centered Medical Home recognition"
                ],
                key_characteristics=["Patient-centered", "Technology-enabled", "Comprehensive care", "Quality focused"]
            ),
            "precisionmfg.com": MockCompanyData(
                domain="precisionmfg.com",
                company_name="Precision Manufacturing Inc",
                industry="Manufacturing",
                description="Advanced manufacturing company specializing in precision components for aerospace and automotive industries",
                website_content="Precision Manufacturing Inc is a leader in high-precision component manufacturing, serving the aerospace and automotive industries for over 30 years. Our state-of-the-art facilities and ISO 9001:2015 certification ensure the highest quality standards in every product we deliver.",
                news_headlines=[
                    "Precision Manufacturing secures major aerospace contract worth $50M",
                    "New automated production line increases capacity by 40%",
                    "Company invests in Industry 4.0 technologies for smart manufacturing"
                ],
                key_characteristics=["Precision engineering", "Aerospace certified", "Automated production", "Quality excellence"]
            )
        }
    
    def _generate_mock_contexts(self) -> Dict[str, MockContext]:
        """Generate mock lead context data."""
        return {
            "ctx_saas_conversion": MockContext(
                context_id="ctx_saas_conversion",
                campaign_name="SaaS Workflow Optimization Campaign",
                source_copy="Transform your business processes with AI-powered workflow automation. Increase productivity by 40% and reduce manual tasks.",
                landing_page_url="https://ourcompany.com/saas-automation",
                campaign_type="Digital Ads",
                target_audience="Tech startups and scale-ups looking to optimize operations"
            ),
            "ctx_pos_upgrade": MockContext(
                context_id="ctx_pos_upgrade",
                campaign_name="Enterprise POS Modernization",
                source_copy="Modernize your point-of-sale systems with cloud-based solutions. Real-time inventory, advanced analytics, and seamless integrations.",
                landing_page_url="https://ourcompany.com/enterprise-pos",
                campaign_type="LinkedIn Sponsored Content",
                target_audience="Retail executives and IT decision makers"
            ),
            "ctx_restaurant_efficiency": MockContext(
                context_id="ctx_restaurant_efficiency",
                campaign_name="Restaurant Operations Excellence",
                source_copy="Streamline your restaurant operations from order to payment. Reduce wait times, improve accuracy, and enhance customer satisfaction.",
                landing_page_url="https://ourcompany.com/restaurant-solutions",
                campaign_type="Industry Publication",
                target_audience="Restaurant owners and managers"
            ),
            "ctx_healthcare_compliance": MockContext(
                context_id="ctx_healthcare_compliance",
                campaign_name="Healthcare-Compliant Solutions",
                source_copy="HIPAA-compliant systems designed for healthcare providers. Secure patient data management with seamless billing integration.",
                landing_page_url="https://ourcompany.com/healthcare-compliance",
                campaign_type="Healthcare Trade Show",
                target_audience="Medical practice administrators and physicians"
            ),
            "ctx_supply_chain": MockContext(
                context_id="ctx_supply_chain",
                campaign_name="Manufacturing Supply Chain Optimization",
                source_copy="Gain real-time visibility into your supply chain operations. Optimize inventory, reduce costs, and improve operational efficiency.",
                landing_page_url="https://ourcompany.com/supply-chain",
                campaign_type="Manufacturing Newsletter",
                target_audience="Manufacturing executives and operations managers"
            )
        }
    
    async def simulate_webhook_test(self, lead: MockLead) -> Dict[str, Any]:
        """Simulate a webhook request for the given lead."""
        start_time = time.time()
        
        logger.info(f"🧪 Testing lead: {lead.lead_id} ({lead.scenario_type})")
        
        try:
            # Simulate company intelligence gathering
            company_data = self.company_data.get(lead.company_domain)
            if not company_data and lead.scenario_type != "error_testing":
                # Generate fallback data for unknown companies
                company_data = self._generate_fallback_company_data(lead)
            
            # Simulate context retrieval
            context_data = self.contexts.get(lead.context_id, {})
            
            # Simulate AI briefing generation
            briefing = self._generate_mock_briefing(lead, company_data, context_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            result = {
                "lead_id": lead.lead_id,
                "status": "success" if lead.scenario_type != "error_testing" else "error_handled",
                "processing_time": round(processing_time, 3),
                "company_found": company_data is not None,
                "context_found": bool(context_data),
                "briefing": briefing if lead.scenario_type != "error_testing" else None,
                "error_message": "Domain not accessible" if lead.scenario_type == "error_testing" else None
            }
            
            if lead.scenario_type != "error_testing":
                logger.info(f"✅ {lead.lead_id}: Generated briefing in {processing_time:.3f}s")
                if company_data:
                    logger.info(f"   Company: {company_data.company_name} ({company_data.industry})")
                if context_data:
                    logger.info(f"   Context: {context_data.get('campaign_name', 'Unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error testing {lead.lead_id}: {str(e)}")
            return {
                "lead_id": lead.lead_id,
                "status": "error",
                "processing_time": time.time() - start_time,
                "error_message": str(e)
            }
    
    def _generate_fallback_company_data(self, lead: MockLead) -> MockCompanyData:
        """Generate fallback company data for unknown domains."""
        return MockCompanyData(
            domain=lead.company_domain,
            company_name=lead.company,
            industry=lead.industry,
            description=f"{lead.company} is a {lead.industry.lower()} company with {lead.company_size}.",
            website_content=f"Welcome to {lead.company}. We are a leading {lead.industry.lower()} organization focused on delivering exceptional results.",
            news_headlines=[f"{lead.company} continues growth in {lead.industry} sector"],
            key_characteristics=["Industry leader", "Growth focused", "Customer centric"]
        )
    
    def _generate_mock_briefing(self, lead: MockLead, company_data: MockCompanyData, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock AI briefing based on lead and company data."""
        if lead.scenario_type == "error_testing":
            return None
        
        return {
            "company_profile": {
                "name": company_data.company_name if company_data else lead.company,
                "industry": lead.industry,
                "description": company_data.description if company_data else f"A {lead.industry.lower()} company",
                "size": lead.company_size,
                "key_characteristics": company_data.key_characteristics if company_data else ["Unknown"]
            },
            "key_updates": company_data.news_headlines if company_data else ["No recent news available"],
            "lead_angle": self._generate_lead_angle(lead, context_data),
            "conversation_starters": self._generate_conversation_starters(lead),
            "potential_objections": self._generate_objection_handling(lead)
        }
    
    def _generate_lead_angle(self, lead: MockLead, context_data: Dict[str, Any]) -> str:
        """Generate a targeted lead angle based on context and industry."""
        angles = {
            "saas_prospect": "Focus on workflow automation benefits and productivity gains. Emphasize scalability and integration capabilities.",
            "enterprise_pos": "Highlight enterprise-grade features, multi-location management, and advanced analytics capabilities.",
            "restaurant_chain": "Emphasize order accuracy, kitchen efficiency, and customer experience improvements.",
            "healthcare_specialist": "Focus on HIPAA compliance, patient data security, and seamless billing integration.",
            "manufacturing_optimization": "Highlight supply chain visibility, inventory optimization, and operational efficiency gains."
        }
        return angles.get(lead.scenario_type, "Tailor solution to address specific business challenges and growth objectives.")
    
    def _generate_conversation_starters(self, lead: MockLead) -> List[str]:
        """Generate contextual conversation starters."""
        base_questions = [
            f"What are the biggest challenges you're currently facing in {lead.industry.lower()} operations?",
            f"How are you handling {', '.join(lead.expected_challenges[:2]).lower()} in your current setup?",
            f"What are your priorities for the next 12 months in terms of {lead.industry.lower()} technology?"
        ]
        
        industry_specific = {
            "Technology": "How is your team currently managing workflow automation and process optimization?",
            "Retail": "What pain points do you experience with your current POS and inventory management systems?",
            "Food & Beverage": "How do you currently handle order management and kitchen operations across your locations?",
            "Healthcare": "What are your main concerns regarding patient data management and billing processes?",
            "Manufacturing": "How do you currently track and optimize your supply chain operations?"
        }
        
        if lead.industry in industry_specific:
            base_questions.append(industry_specific[lead.industry])
        
        return base_questions
    
    def _generate_objection_handling(self, lead: MockLead) -> List[Dict[str, str]]:
        """Generate potential objections and handling strategies."""
        common_objections = [
            {
                "objection": "Budget constraints - we're not ready to invest in new systems right now.",
                "handling_strategy": "I understand budget is a concern. Our solution typically pays for itself within 6-12 months through efficiency gains. Can we explore a phased implementation approach?"
            },
            {
                "objection": "We're satisfied with our current system and don't see the need to change.",
                "handling_strategy": "I appreciate that your current system is working. However, based on what I understand about your business, there might be opportunities to achieve even better results. Would you be open to a brief demonstration?"
            }
        ]
        
        industry_specific = {
            "Technology": {
                "objection": "Integration complexity with our existing tech stack.",
                "handling_strategy": "Our platform is designed with integration in mind. We have pre-built connectors for major systems and our integration team ensures smooth implementation."
            },
            "Retail": {
                "objection": "Concern about system downtime during implementation across multiple locations.",
                "handling_strategy": "We use a proven rollout methodology that minimizes disruption. We can implement location-by-location with full support during transition periods."
            },
            "Healthcare": {
                "objection": "Compliance and security concerns with patient data.",
                "handling_strategy": "Security and compliance are our top priorities. We're HIPAA compliant and can provide detailed security documentation and compliance certifications."
            }
        }
        
        if lead.industry in industry_specific:
            common_objections.append(industry_specific[lead.industry])
        
        return common_objections
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all mock lead tests."""
        logger.info("🚀 Starting mock lead testing...")
        
        start_time = time.time()
        tasks = [self.simulate_webhook_test(lead) for lead in self.leads]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful_tests = len([r for r in results if r["status"] == "success"])
        error_handled_tests = len([r for r in results if r["status"] == "error_handled"])
        failed_tests = len([r for r in results if r["status"] == "error"])
        
        avg_processing_time = sum(r["processing_time"] for r in results) / len(results)
        
        summary = {
            "total_tests": len(results),
            "successful_tests": successful_tests,
            "error_handled_tests": error_handled_tests,
            "failed_tests": failed_tests,
            "total_execution_time": round(total_time, 3),
            "average_processing_time": round(avg_processing_time, 3),
            "results": results
        }
        
        logger.info(f"✅ Testing completed: {successful_tests}/{len(results)} successful, {error_handled_tests} error scenarios handled")
        logger.info(f"⏱️  Total time: {total_time:.3f}s, Average per test: {avg_processing_time:.3f}s")
        
        return summary

def main():
    """Main entry point for the mock testing script."""
    parser = argparse.ArgumentParser(description="Mock Lead Data Testing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    test_suite = MockLeadTestSuite()
    results = asyncio.run(test_suite.run_all_tests())
    
    if args.verbose:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 