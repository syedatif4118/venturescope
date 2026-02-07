"""Investment Memo Generator - Synthesizes all analyses into a final memo."""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from core.llm_client import HuggingFaceLLMClient

logger = logging.getLogger(__name__)


class MemoGeneratorAgent:
    """Agent responsible for generating final investment memos."""
    
    SYSTEM_PROMPT = """You are a senior partner at a top-tier venture capital firm.
Your role is to synthesize investment analyses into clear, actionable investment memos.

Your memos should:
- Lead with a clear recommendation (PASS, CONSIDER, STRONG CONSIDER, INVEST)
- Provide executive summary with key highlights
- Balance optimism with realism
- Cite specific evidence from analyses
- Be concise yet comprehensive
- Follow a standard memo format

Write for a sophisticated audience of investors who value directness and data."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        logger.info("Initialized MemoGeneratorAgent")
    
    def process(
        self,
        company_data: Dict[str, Any],
        all_analyses: Dict[str, Any],
        final_score: int,
    ) -> Dict[str, Any]:
        """Generate comprehensive investment memo.
        
        Args:
            company_data: Original company data
            all_analyses: All agent analyses
            final_score: Final investment score (0-100)
            
        Returns:
            Investment memo
        """
        company_name = company_data.get("enhanced_data", {}).get("company_name", "Unknown")
        logger.info(f"Generating investment memo for: {company_name}")
        
        # Generate recommendation
        recommendation = self._determine_recommendation(final_score, all_analyses)
        
        # Generate memo
        memo = self._generate_memo(
            company_name=company_name,
            company_data=company_data,
            all_analyses=all_analyses,
            final_score=final_score,
            recommendation=recommendation,
        )
        
        result = {
            "memo": memo,
            "recommendation": recommendation,
            "final_score": final_score,
            "generated_at": datetime.now().isoformat(),
        }
        
        logger.info(f"Investment memo complete. Recommendation: {recommendation}")
        return result
    
    def _determine_recommendation(self, final_score: int, all_analyses: Dict[str, Any]) -> str:
        """Determine investment recommendation based on score and risks.
        
        Args:
            final_score: Total score (0-100)
            all_analyses: All analyses
            
        Returns:
            Recommendation: PASS, CONSIDER, STRONG CONSIDER, or INVEST
        """
        # Check for critical red flags
        risk_data = all_analyses.get("risk", {})
        critical_flags = risk_data.get("critical_flags", [])
        has_critical = len(critical_flags) > 0
        
        if has_critical:
            return "PASS"
        elif final_score >= 80:
            return "INVEST"
        elif final_score >= 65:
            return "STRONG CONSIDER"
        elif final_score >= 50:
            return "CONSIDER"
        else:
            return "PASS"
    
    def _generate_memo(
        self,
        company_name: str,
        company_data: Dict[str, Any],
        all_analyses: Dict[str, Any],
        final_score: int,
        recommendation: str,
    ) -> str:
        """Generate full investment memo using LLM.
        
        Returns:
            Formatted investment memo (Markdown)
        """
        # Extract key data
        enhanced = company_data.get("enhanced_data", {})
        market = all_analyses.get("market", {})
        team = all_analyses.get("team", {})
        financial = all_analyses.get("financial", {})
        risk = all_analyses.get("risk", {})
        
        # Prepare context for LLM
        context = f"""Company: {company_name}
Tagline: {enhanced.get('tagline', 'Not specified')}
Solution: {enhanced.get('solution', 'Not specified')}

Final Score: {final_score}/100
Recommendation: {recommendation}

SCORE BREAKDOWN:
- Market: {market.get('score', 0)}/25
- Team: {team.get('score', 0)}/25
- Financials: {financial.get('score', 0)}/25
- Execution: {max(0, final_score - market.get('score', 0) - team.get('score', 0) - financial.get('score', 0))}/25

MARKET ANALYSIS:
{market.get('analysis', {}).get('full_analysis', 'Not available')[:500]}

TEAM ASSESSMENT:
{team.get('assessment', {}).get('full_assessment', 'Not available')[:500]}

FINANCIAL ANALYSIS:
{financial.get('analysis', {}).get('full_analysis', 'Not available')[:500]}

RISK ASSESSMENT:
Critical Flags: {', '.join(risk.get('critical_flags', []))}
Risk Level: {risk.get('risk_level', 'Unknown')}
"""
        
        prompt = f"""Generate a professional investment memo based on this analysis:

{context}

Format the memo as follows:

# Investment Memo: [Company Name]

## Executive Summary
**Investment Score:** {final_score}/100 | **Recommendation:** {recommendation}

[2-3 sentence summary of the opportunity and recommendation]

## Key Highlights
✅ [3-5 positive bullet points]
⚠️ [2-3 concerns/risks]

## Market Opportunity (Score: X/25)
[2-3 paragraphs on market size, growth, and competitive position]

## Team Assessment (Score: X/25)
[2-3 paragraphs on team quality, experience, and gaps]

## Financial Analysis (Score: X/25)
[2-3 paragraphs on traction, projections, and unit economics]

## Risk Analysis
**Risk Level:** [LEVEL]

**Key Risks:**
- [List top 3-5 risks]

**Mitigation Strategies:**
- [List 2-3 mitigation approaches]

## Investment Rationale
[2-3 paragraphs on why this is/isn't a good investment]

## Recommendation
**{recommendation}**

[Final 2-3 sentences with clear next steps]

---
*Memo generated by VentureScope AI | {datetime.now().strftime('%B %d, %Y')}*

Write in a professional but direct tone. Be data-driven and specific.
"""
        
        try:
            memo = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=2500,
                temperature=0.5,
            )
            return memo
        except Exception as e:
            logger.error(f"Error generating memo: {str(e)}")
            # Return a basic memo template
            return self._generate_fallback_memo(company_name, final_score, recommendation)
    
    def _generate_fallback_memo(self, company_name: str, final_score: int, recommendation: str) -> str:
        """Generate basic memo if LLM fails.
        
        Returns:
            Basic memo template
        """
        return f"""# Investment Memo: {company_name}

## Executive Summary
**Investment Score:** {final_score}/100 | **Recommendation:** {recommendation}

Analysis completed but detailed memo generation encountered an error.
Please review individual agent reports for detailed insights.

## Recommendation
**{recommendation}**

Based on quantitative scoring: {final_score}/100

---
*Memo generated by VentureScope AI | {datetime.now().strftime('%B %d, %Y')}*
"""
