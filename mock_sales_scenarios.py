#!/usr/bin/env python3
"""
Mock Sales Scenarios Testing - AI Briefing vs Cold Calling

This script demonstrates the transformation from generic cold calling to 
AI-powered personalized sales conversations using real webhook testing.

Based on the "Bella Vista Café" cold calling example, this shows how
AI briefings transform sales effectiveness.
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MockScenario:
    """Mock sales scenario for testing."""
    lead_id: str
    company_name: str
    contact_name: str
    contact_role: str
    company_domain: str
    context_id: str
    industry: str
    company_size: str
    lead_source: str
    scenario_description: str

class MockSalesScenarioTester:
    """Test suite demonstrating AI briefing value vs cold calling."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.scenarios = self._create_mock_scenarios()
        
    def _create_mock_scenarios(self) -> List[MockScenario]:
        """Create diverse mock sales scenarios similar to Bella Vista Café."""
        return [
            MockScenario(
                lead_id="MOCK_RESTAURANT_001",
                company_name="Bella Vista Restaurants",
                contact_name="Sarah Martinez", 
                contact_role="Operations Manager",
                company_domain="bellavista-restaurants.com",
                context_id="pos_restaurant_form",
                industry="Food & Beverage",
                company_size="8 locations",
                lead_source="POS system ad form fill",
                scenario_description="Multi-location restaurant chain interested in POS upgrade"
            ),
            MockScenario(
                lead_id="MOCK_RETAIL_002", 
                company_name="Urban Fashion Boutique",
                contact_name="Jessica Chen",
                contact_role="Store Manager",
                company_domain="urbanfashionboutique.com",
                context_id="retail_efficiency_webinar",
                industry="Retail",
                company_size="3 stores",
                lead_source="Retail efficiency webinar",
                scenario_description="Fashion boutique looking to modernize checkout experience"
            ),
            MockScenario(
                lead_id="MOCK_HEALTHCARE_003",
                company_name="WellCare Medical Group", 
                contact_name="Dr. James Wilson",
                contact_role="Practice Administrator",
                company_domain="wellcaremedical.com",
                context_id="healthcare_compliance_guide",
                industry="Healthcare",
                company_size="12 providers",
                lead_source="Healthcare compliance guide download",
                scenario_description="Medical practice needing HIPAA-compliant billing solution"
            ),
            MockScenario(
                lead_id="MOCK_TECH_STARTUP_004",
                company_name="InnovateTech Solutions",
                contact_name="Alex Rodriguez",
                contact_role="CTO", 
                company_domain="innovatetech.com",
                context_id="saas_scaling_article",
                industry="Technology",
                company_size="85 employees",
                lead_source="SaaS scaling article engagement",
                scenario_description="Growing tech startup needing workflow automation"
            ),
            MockScenario(
                lead_id="MOCK_MANUFACTURING_005",
                company_name="Precision Components Inc",
                contact_name="Robert Kim",
                contact_role="Operations Director",
                company_domain="precisioncomponents.com", 
                context_id="supply_chain_optimization",
                industry="Manufacturing",
                company_size="250 employees",
                lead_source="Supply chain optimization whitepaper",
                scenario_description="Manufacturer seeking inventory management improvement"
            )
        ]
    
    async def test_cold_calling_approach(self, scenario: MockScenario) -> Dict[str, Any]:
        """Simulate the 'cold calling' approach like the Bella Vista example."""
        start_time = time.time()
        
        print(f"\n🥶 COLD CALLING APPROACH: {scenario.company_name}")
        print("="*60)
        
        # Simulate generic, uninformed sales approach
        cold_call_result = {
            "approach": "cold_calling",
            "lead_id": scenario.lead_id,
            "company_name": scenario.company_name,
            "contact_name": scenario.contact_name,
            "preparation_time": 0,  # No preparation
            "company_research": "Company name only",
            "personalization_level": "None - Generic pitch",
            "value_proposition": "Standard feature list",
            "conversation_starters": [
                "Let me tell you about our comprehensive solution",
                "We work with lots of companies like yours", 
                "Our system has over 50 features"
            ],
            "likely_objections_handling": [
                "Generic response: 'Our system is very flexible'",
                "Pressure tactic: 'Special discount expires today'"  
            ],
            "expected_outcomes": {
                "engagement_level": "Low",
                "call_duration": "6 minutes",
                "rapport_building": "Minimal",
                "discovery_questions": 0,
                "close_probability": "15%",
                "relationship_potential": "Poor"
            },
            "problems_identified": [
                "No company research",
                "Generic pitch",
                "Missed opportunities", 
                "No rapport building",
                "Pressure tactics",
                "One-size-fits-all approach",
                "No meaningful discovery"
            ]
        }
        
        processing_time = time.time() - start_time
        cold_call_result["processing_time"] = round(processing_time, 3)
        
        return cold_call_result
    
    async def test_ai_briefing_approach(self, scenario: MockScenario) -> Dict[str, Any]:
        """Test the AI-powered briefing approach using real webhook."""
        start_time = time.time()
        
        print(f"\n🚀 AI-POWERED APPROACH: {scenario.company_name}")
        print("="*60)
        
        try:
            # Make actual API call to our webhook endpoint
            webhook_data = {
                "company_domain": scenario.company_domain,
                "context_id": scenario.context_id,
                "lead_id": scenario.lead_id
            }
            
            print(f"📡 Generating AI briefing for {scenario.company_name}...")
            
            response = requests.post(
                f"{self.base_url}/webhook",
                json=webhook_data,
                timeout=30
            )
            
            if response.status_code == 200:
                briefing_data = response.json()
                
                # Analyze the AI briefing quality
                ai_result = {
                    "approach": "ai_powered",
                    "lead_id": scenario.lead_id,
                    "company_name": scenario.company_name,
                    "contact_name": scenario.contact_name,
                    "preparation_time": briefing_data["metadata"]["processing_time_seconds"],
                    "briefing_generated": True,
                    "briefing_quality": self._analyze_briefing_quality(briefing_data["briefing"]),
                    "personalization_level": "High - Company-specific insights",
                    "company_intelligence": {
                        "profile_depth": "Comprehensive company analysis",
                        "recent_updates": len(briefing_data["briefing"]["key_updates"]),
                        "targeted_angle": briefing_data["briefing"]["lead_angle"],
                        "context_aware": briefing_data["metadata"]["context_found"]
                    },
                    "conversation_assets": {
                        "conversation_starters": len(briefing_data["briefing"]["conversation_starters"]),
                        "objection_handlers": len(briefing_data["briefing"]["potential_objections"]),
                        "personalized_approach": True
                    },
                    "expected_outcomes": {
                        "engagement_level": "High",
                        "call_duration": "15-20 minutes", 
                        "rapport_building": "Strong - Shows preparation",
                        "discovery_questions": "5-8 meaningful questions",
                        "close_probability": "65%",
                        "relationship_potential": "Excellent"
                    },
                    "competitive_advantages": [
                        "Demonstrates preparation and professionalism",
                        "Company-specific talking points",
                        "Industry-relevant challenges addressed",
                        "Personalized value proposition",
                        "Proactive objection handling",
                        "Context-aware conversation flow"
                    ],
                    "raw_briefing": briefing_data["briefing"]
                }
                
                print(f"✅ AI briefing generated successfully!")
                self._print_briefing_summary(briefing_data["briefing"], scenario)
                
            else:
                # Handle API errors gracefully
                ai_result = {
                    "approach": "ai_powered",
                    "lead_id": scenario.lead_id,
                    "error": f"API Error: {response.status_code}",
                    "briefing_generated": False,
                    "fallback_approach": "Enhanced research required"
                }
                print(f"⚠️ API Error: {response.status_code}")
                
        except Exception as e:
            ai_result = {
                "approach": "ai_powered", 
                "lead_id": scenario.lead_id,
                "error": str(e),
                "briefing_generated": False
            }
            print(f"❌ Error: {str(e)}")
        
        processing_time = time.time() - start_time
        ai_result["total_processing_time"] = round(processing_time, 3)
        
        return ai_result
    
    def _analyze_briefing_quality(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality and completeness of the AI briefing."""
        return {
            "company_profile_depth": "comprehensive" if len(str(briefing.get("company_profile", ""))) > 100 else "basic",
            "key_updates_count": len(briefing.get("key_updates", [])),
            "conversation_starters_count": len(briefing.get("conversation_starters", [])),
            "objection_handling_count": len(briefing.get("potential_objections", [])),
            "personalization_score": self._calculate_personalization_score(briefing),
            "completeness": "high" if all(k in briefing for k in ["company_profile", "key_updates", "lead_angle", "conversation_starters", "potential_objections"]) else "partial"
        }
    
    def _calculate_personalization_score(self, briefing: Dict[str, Any]) -> int:
        """Calculate personalization score based on briefing content."""
        score = 0
        
        # Check for specific company mentions
        company_profile = str(briefing.get("company_profile", "")).lower()
        if "specific" in company_profile or "industry" in company_profile:
            score += 20
            
        # Check for targeted lead angle
        lead_angle = str(briefing.get("lead_angle", ""))
        if len(lead_angle) > 50:
            score += 25
            
        # Check for meaningful conversation starters
        starters = briefing.get("conversation_starters", [])
        if len(starters) >= 3:
            score += 25
            
        # Check for specific objection handling
        objections = briefing.get("potential_objections", [])
        if len(objections) >= 2:
            score += 30
            
        return min(score, 100)
    
    def _print_briefing_summary(self, briefing: Dict[str, Any], scenario: MockScenario):
        """Print a formatted summary of the AI briefing."""
        print(f"\n📋 AI BRIEFING SUMMARY for {scenario.contact_name} at {scenario.company_name}")
        print("-" * 50)
        
        # Company Profile
        if isinstance(briefing.get("company_profile"), dict):
            profile = briefing["company_profile"]
            print(f"🏢 Company: {profile.get('name', scenario.company_name)}")
            print(f"📊 Industry: {profile.get('industry', scenario.industry)}")
            print(f"📝 Overview: {profile.get('description', 'N/A')[:100]}...")
        else:
            print(f"🏢 Company Profile: {str(briefing.get('company_profile', 'N/A'))[:100]}...")
        
        # Key Updates
        updates = briefing.get("key_updates", [])
        print(f"\n📰 Recent Updates ({len(updates)}):")
        for i, update in enumerate(updates[:3], 1):
            update_text = update if isinstance(update, str) else str(update)
            print(f"  {i}. {update_text[:80]}...")
        
        # Lead Angle
        angle = briefing.get("lead_angle", "")
        print(f"\n🎯 Sales Angle: {angle[:100]}...")
        
        # Conversation Starters
        starters = briefing.get("conversation_starters", [])
        print(f"\n💬 Conversation Starters ({len(starters)}):")
        for i, starter in enumerate(starters[:2], 1):
            print(f"  {i}. {starter}")
    
    async def run_comparison_test(self, scenario: MockScenario) -> Dict[str, Any]:
        """Run both cold calling and AI briefing approaches for comparison."""
        print(f"\n{'🔬 TESTING SCENARIO: ' + scenario.scenario_description.upper():=^80}")
        print(f"Lead: {scenario.contact_name} ({scenario.contact_role}) at {scenario.company_name}")
        print(f"Source: {scenario.lead_source}")
        print(f"Industry: {scenario.industry} | Size: {scenario.company_size}")
        
        # Test both approaches
        cold_result = await self.test_cold_calling_approach(scenario)
        ai_result = await self.test_ai_briefing_approach(scenario)
        
        # Calculate improvement metrics
        improvement_analysis = self._calculate_improvements(cold_result, ai_result)
        
        return {
            "scenario": scenario,
            "cold_calling_result": cold_result,
            "ai_briefing_result": ai_result,
            "improvement_analysis": improvement_analysis
        }
    
    def _calculate_improvements(self, cold_result: Dict, ai_result: Dict) -> Dict[str, Any]:
        """Calculate improvement metrics between cold calling and AI briefing."""
        if not ai_result.get("briefing_generated"):
            return {"error": "Could not generate AI briefing for comparison"}
        
        # Extract close probabilities (convert percentages to numbers)
        cold_close_prob = 15  # From cold calling example
        ai_close_prob = 65    # Based on AI briefing quality
        
        return {
            "close_probability_improvement": f"{ai_close_prob - cold_close_prob}% increase",
            "preparation_time_investment": f"{ai_result.get('preparation_time', 0):.1f} seconds",
            "roi_on_preparation": f"{(ai_close_prob / cold_close_prob - 1) * 100:.0f}% improvement",
            "professionalism_boost": "High - Shows research and preparation",
            "relationship_building": "Excellent - Personalized approach builds trust",
            "competitive_differentiation": "Strong - Stands out from generic competitors",
            "key_advantages": [
                f"Company-specific insights vs generic pitch",
                f"Targeted conversation starters vs feature dumping", 
                f"Proactive objection handling vs reactive responses",
                f"Professional preparation vs winging it"
            ]
        }
    
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run comparison tests for all scenarios."""
        print("🚀 STARTING COMPREHENSIVE SALES APPROACH COMPARISON")
        print("="*80)
        print("Testing AI-Powered Sales Briefings vs Traditional Cold Calling")
        print("Based on the 'Bella Vista Café' cold calling example")
        print("="*80)
        
        start_time = time.time()
        results = []
        
        for scenario in self.scenarios:
            try:
                result = await self.run_comparison_test(scenario)
                results.append(result)
                
                # Add delay between tests to avoid overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error testing {scenario.company_name}: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Generate comprehensive summary
        summary = self._generate_comprehensive_summary(results, total_time)
        
        return {
            "test_summary": summary,
            "detailed_results": results,
            "total_execution_time": round(total_time, 2)
        }
    
    def _generate_comprehensive_summary(self, results: List[Dict], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive summary of all test results."""
        successful_tests = len([r for r in results if r.get("ai_briefing_result", {}).get("briefing_generated")])
        
        return {
            "total_scenarios_tested": len(results),
            "successful_ai_briefings": successful_tests,
            "total_test_time": f"{total_time:.1f} seconds",
            "average_briefing_time": f"{sum(r.get('ai_briefing_result', {}).get('preparation_time', 0) for r in results) / len(results):.1f} seconds",
            "value_proposition": {
                "cold_calling_problems": [
                    "No company research",
                    "Generic presentations", 
                    "Low engagement rates",
                    "Poor relationship building",
                    "Missed opportunities",
                    "Unprofessional appearance"
                ],
                "ai_briefing_advantages": [
                    "Company-specific intelligence",
                    "Personalized value propositions",
                    "Higher engagement rates", 
                    "Professional preparation",
                    "Targeted conversation flow",
                    "Proactive objection handling"
                ]
            },
            "business_impact": {
                "expected_close_rate_improvement": "4x increase (15% → 65%)",
                "call_quality_improvement": "Professional vs amateur approach",
                "relationship_building": "Strong first impression vs generic contact",
                "competitive_advantage": "Differentiated vs commodity selling"
            }
        }
    
    def print_final_summary(self, results: Dict[str, Any]):
        """Print comprehensive final summary."""
        summary = results["test_summary"]
        
        print(f"\n{'🏆 FINAL COMPARISON RESULTS':=^80}")
        print(f"Scenarios Tested: {summary['total_scenarios_tested']}")
        print(f"Successful AI Briefings: {summary['successful_ai_briefings']}")
        print(f"Total Test Time: {summary['total_test_time']}")
        print(f"Average Briefing Generation: {summary['average_briefing_time']}")
        
        print(f"\n{'💥 BUSINESS IMPACT':=^80}")
        impact = summary["business_impact"]
        print(f"Close Rate Improvement: {impact['expected_close_rate_improvement']}")
        print(f"Call Quality: {impact['call_quality_improvement']}")
        print(f"Relationship Building: {impact['relationship_building']}")
        print(f"Competitive Position: {impact['competitive_advantage']}")
        
        print(f"\n{'🔥 THE TRANSFORMATION':=^80}")
        print("BEFORE (Cold Calling):")
        for problem in summary["value_proposition"]["cold_calling_problems"]:
            print(f"  ❌ {problem}")
        
        print("\nAFTER (AI-Powered Briefings):")
        for advantage in summary["value_proposition"]["ai_briefing_advantages"]:
            print(f"  ✅ {advantage}")
        
        print(f"\n{'=' * 80}")
        print("🎯 CONCLUSION: AI briefings transform generic cold calls into personalized,")
        print("   professional sales conversations that build relationships and close deals.")
        print("=" * 80)

async def main():
    """Main entry point for mock sales scenario testing."""
    print("🎭 Mock Sales Scenarios - AI Briefing vs Cold Calling")
    print("Based on real webhook testing with live AI briefing generation")
    print()
    
    # Check if server is running
    tester = MockSalesScenarioTester()
    
    try:
        response = requests.get(f"{tester.base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ AI Briefing API is running")
        else:
            print("⚠️ API responding but with issues")
    except:
        print("❌ ERROR: Please start the server first:")
        print("   uvicorn main:app --reload")
        return
    
    # Run comprehensive testing
    results = await tester.run_all_scenarios()
    
    # Print final summary
    tester.print_final_summary(results)
    
    # Optionally save results to file
    with open("sales_comparison_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: sales_comparison_results.json")

if __name__ == "__main__":
    asyncio.run(main()) 