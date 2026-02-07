"""Market Analysis Agent - Researches market size, trends, and competition."""

from typing import Dict, Any, List, Optional
import logging

from core.llm_client import HuggingFaceLLMClient
from utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class MarketAnalysisAgent:
    """Agent responsible for market research and competitive analysis."""
    
    SYSTEM_PROMPT = """You are a market research analyst specializing in startup ecosystems.
Your role is to analyze market opportunities, validate market size claims, and assess competitive landscapes.

Focus on:
- Total Addressable Market (TAM) validation
- Market growth trends and CAGR
- Competitive landscape analysis
- Market positioning and differentiation
- Barriers to entry
- Market risks and opportunities

Provide data-driven insights with realistic assessments. Be skeptical of inflated claims."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        self.web_scraper = WebScraper()
        logger.info("Initialized MarketAnalysisAgent")
    
    def process(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market opportunity and competitive landscape.
        
        Args:
            company_data: Data from DocumentIngestionAgent
            
        Returns:
            Market analysis results
        """
        company_name = company_data.get("enhanced_data", {}).get("company_name", "Unknown")
        logger.info(f"Analyzing market for: {company_name}")
        
        # Extract relevant info
        enhanced = company_data.get("enhanced_data", {})
        solution = enhanced.get("solution", "")
        market_size_claim = enhanced.get("market_size", "")
        competitors = enhanced.get("competitors", [])
        
        # Infer industry from solution
        industry = self._infer_industry(solution)
        
        # Gather market intelligence
        market_research = self.web_scraper.search_market_size(industry)
        competitor_research = self._research_competitors(company_name, industry, competitors)
        
        # LLM analysis
        analysis = self._generate_market_analysis(
            company_name=company_name,
            solution=solution,
            market_size_claim=market_size_claim,
            industry=industry,
            market_research=market_research,
            competitor_research=competitor_research,
        )
        
        result = {
            "industry": industry,
            "market_research": market_research,
            "competitor_research": competitor_research,
            "analysis": analysis,
            "score": self._calculate_market_score(analysis),
        }
        
        logger.info(f"Market analysis complete. Score: {result['score']}/25")
        return result
    
    def _infer_industry(self, solution: str) -> str:
        """Infer industry from solution description.
        
        Args:
            solution: Solution/product description
            
        Returns:
            Industry name
        """
        # Simple keyword matching
        solution_lower = solution.lower()
        
        if any(word in solution_lower for word in ["health", "medical", "patient", "doctor"]):
            return "Healthcare"
        elif any(word in solution_lower for word in ["finance", "payment", "banking", "fintech"]):
            return "Fintech"
        elif any(word in solution_lower for word in ["education", "learning", "school", "student"]):
            return "Edtech"
        elif any(word in solution_lower for word in ["ecommerce", "retail", "shopping", "marketplace"]):
            return "E-commerce"
        elif any(word in solution_lower for word in ["saas", "software", "platform", "cloud"]):
            return "SaaS"
        elif any(word in solution_lower for word in ["ai", "machine learning", "artificial intelligence"]):
            return "AI/ML"
        else:
            return "Technology"
    
    def _research_competitors(self, company_name: str, industry: str, known_competitors: List[str]) -> Dict[str, Any]:
        """Research competitors in the market.
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            known_competitors: Competitors mentioned in pitch deck
            
        Returns:
            Competitor research results
        """
        # Search for competitors
        search_results = self.web_scraper.search_competitors(company_name, industry)
        
        return {
            "known_competitors": known_competitors if isinstance(known_competitors, list) else [],
            "discovered_competitors": search_results[:5],
            "competitive_intensity": "High" if len(search_results) > 3 else "Medium",
        }
    
    def _generate_market_analysis(
        self,
        company_name: str,
        solution: str,
        market_size_claim: str,
        industry: str,
        market_research: Dict[str, Any],
        competitor_research: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive market analysis using LLM.
        
        Returns:
            Analysis with TAM validation, trends, competitive assessment
        """
        prompt = f"""Analyze the market opportunity for this startup:

Company: {company_name}
Industry: {industry}
Solution: {solution}

Market Size Claim: {market_size_claim}

Market Research:
{market_research.get('summary', 'Limited data available')}

Known Competitors: {', '.join(competitor_research.get('known_competitors', []))}
Competitive Intensity: {competitor_research.get('competitive_intensity', 'Unknown')}

Provide analysis on:

1. TAM Validation: Is the claimed market size realistic? (2-3 sentences)
2. Market Growth: What are the growth trends and drivers? (2-3 sentences)
3. Competitive Position: How differentiated is this solution? (2-3 sentences)
4. Market Risks: What are the key risks? (2-3 sentences)
5. Market Score: Rate the market opportunity from 0-25 points based on size, growth, and competition.

Be realistic and data-driven in your assessment.
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1200,
                temperature=0.4,
            )
            
            return {
                "tam_validation": self._extract_section(response, "TAM Validation"),
                "market_growth": self._extract_section(response, "Market Growth"),
                "competitive_position": self._extract_section(response, "Competitive Position"),
                "market_risks": self._extract_section(response, "Market Risks"),
                "market_score": self._extract_score(response),
                "full_analysis": response,
            }
        except Exception as e:
            logger.error(f"Error generating market analysis: {str(e)}")
            return {
                "tam_validation": "Unable to validate",
                "market_growth": "Data unavailable",
                "competitive_position": "Unclear",
                "market_risks": "Analysis failed",
                "market_score": 15,  # Default middle score
                "error": str(e),
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section from LLM response."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if section_name in line:
                # Get next non-empty line
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith(str(j)):
                        return lines[j].strip()
        return "Not specified"
    
    def _extract_score(self, text: str) -> int:
        """Extract market score from LLM response."""
        import re
        # Look for patterns like "Score: 18/25" or "18 points"
        match = re.search(r'(\d+)\s*(?:/25|points|out of 25)', text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 0), 25)  # Clamp between 0-25
        return 15  # Default
    
    def _calculate_market_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate final market score.
        
        Returns:
            Score out of 25
        """
        # Use LLM-generated score if available
        return analysis.get("market_score", 15)
