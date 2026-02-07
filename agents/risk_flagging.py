"""Risk Flagging Agent - Identifies red flags and potential concerns."""

from typing import Dict, Any, List, Optional
import logging

from core.llm_client import HuggingFaceLLMClient

logger = logging.getLogger(__name__)


class RiskFlaggingAgent:
    """Agent responsible for identifying risks and red flags."""
    
    SYSTEM_PROMPT = """You are a risk assessment specialist and due diligence expert.
Your role is to identify potential red flags, risks, and concerns in startup investments.

Focus on:
- Market risks (competition, timing, regulatory)
- Team risks (experience gaps, conflict, turnover)
- Financial risks (burn rate, unit economics, fraud)
- Product risks (technical feasibility, market fit)
- Execution risks (timeline, dependencies, assumptions)
- Legal/regulatory risks
- Reputational risks

Be thorough but balanced. Not every risk is a deal-breaker, but investors need full visibility."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        logger.info("Initialized RiskFlaggingAgent")
    
    def process(self, company_data: Dict[str, Any], previous_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Identify risks and red flags from all previous analyses.
        
        Args:
            company_data: Original company data
            previous_analyses: Results from market, team, financial agents
            
        Returns:
            Risk assessment results
        """
        company_name = company_data.get("enhanced_data", {}).get("company_name", "Unknown")
        logger.info(f"Identifying risks for: {company_name}")
        
        # Collect insights from previous agents
        market_analysis = previous_analyses.get("market", {})
        team_assessment = previous_analyses.get("team", {})
        financial_analysis = previous_analyses.get("financial", {})
        
        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(
            company_name=company_name,
            company_data=company_data,
            market_analysis=market_analysis,
            team_assessment=team_assessment,
            financial_analysis=financial_analysis,
        )
        
        # Categorize risks
        categorized_risks = self._categorize_risks(risk_assessment)
        
        result = {
            "risk_assessment": risk_assessment,
            "categorized_risks": categorized_risks,
            "risk_level": self._determine_risk_level(categorized_risks),
            "critical_flags": self._identify_critical_flags(categorized_risks),
        }
        
        logger.info(f"Risk assessment complete. Level: {result['risk_level']}")
        return result
    
    def _generate_risk_assessment(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        market_analysis: Dict[str, Any],
        team_assessment: Dict[str, Any],
        financial_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive risk assessment using LLM.
        
        Returns:
            Risk assessment with identified concerns
        """
        # Summarize previous analyses
        enhanced = company_data.get("enhanced_data", {})
        
        market_summary = market_analysis.get("analysis", {}).get("market_risks", "Not analyzed")
        team_summary = team_assessment.get("assessment", {}).get("team_gaps", "Not analyzed")
        financial_summary = financial_analysis.get("analysis", {}).get("financial_risks", "Not analyzed")
        
        prompt = f"""Conduct a comprehensive risk assessment for this startup investment:

Company: {company_name}
Solution: {enhanced.get('solution', 'Not specified')}

Market Risks Identified:
{market_summary}

Team Gaps/Concerns:
{team_summary}

Financial Risks:
{financial_summary}

Provide a structured risk assessment:

1. CRITICAL RED FLAGS: Any deal-breaker issues? (List specific flags or "None identified")
2. HIGH RISKS: Significant concerns that need mitigation (3-5 bullet points)
3. MEDIUM RISKS: Notable concerns worth monitoring (3-5 bullet points)
4. LOW RISKS: Minor concerns (2-3 bullet points)
5. RISK MITIGATION: What actions could reduce these risks? (3-4 recommendations)

Be thorough and specific. Cite evidence from the analyses.
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for factual risk assessment
            )
            
            return {
                "critical_flags": self._extract_list_section(response, "CRITICAL RED FLAGS"),
                "high_risks": self._extract_list_section(response, "HIGH RISKS"),
                "medium_risks": self._extract_list_section(response, "MEDIUM RISKS"),
                "low_risks": self._extract_list_section(response, "LOW RISKS"),
                "mitigation": self._extract_list_section(response, "RISK MITIGATION"),
                "full_assessment": response,
            }
        except Exception as e:
            logger.error(f"Error generating risk assessment: {str(e)}")
            return {
                "critical_flags": ["Analysis failed - unable to assess risks"],
                "high_risks": [],
                "medium_risks": [],
                "low_risks": [],
                "mitigation": [],
                "error": str(e),
            }
    
    def _extract_list_section(self, text: str, section_name: str) -> List[str]:
        """Extract bullet point list from section.
        
        Args:
            text: Full text
            section_name: Section header to find
            
        Returns:
            List of bullet points
        """
        lines = text.split('\n')
        items = []
        in_section = False
        
        for line in lines:
            if section_name in line:
                in_section = True
                continue
            
            if in_section:
                # Check if we hit next section
                if line.strip() and line.strip()[0].isdigit() and '.' in line:
                    break
                
                # Extract bullet points
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    items.append(line[1:].strip())
                elif line and len(items) == 0 and not line.startswith(('1.', '2.', '3.')):
                    # First line might not have bullet
                    items.append(line)
        
        return items if items else ["None identified"]
    
    def _categorize_risks(self, risk_assessment: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize risks by type and severity.
        
        Returns:
            Categorized risk dictionary
        """
        return {
            "critical": risk_assessment.get("critical_flags", []),
            "high": risk_assessment.get("high_risks", []),
            "medium": risk_assessment.get("medium_risks", []),
            "low": risk_assessment.get("low_risks", []),
            "mitigation": risk_assessment.get("mitigation", []),
        }
    
    def _determine_risk_level(self, categorized_risks: Dict[str, List[str]]) -> str:
        """Determine overall risk level.
        
        Returns:
            Risk level: CRITICAL, HIGH, MEDIUM, or LOW
        """
        critical = categorized_risks.get("critical", [])
        high = categorized_risks.get("high", [])
        
        # Check if any critical flags (excluding "None identified")
        has_critical = any(flag != "None identified" for flag in critical)
        if has_critical:
            return "CRITICAL"
        
        # Check number of high risks
        if len([r for r in high if r != "None identified"]) >= 3:
            return "HIGH"
        elif len([r for r in high if r != "None identified"]) >= 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_critical_flags(self, categorized_risks: Dict[str, List[str]]) -> List[str]:
        """Identify deal-breaker flags.
        
        Returns:
            List of critical flags
        """
        critical = categorized_risks.get("critical", [])
        return [flag for flag in critical if flag != "None identified"]
