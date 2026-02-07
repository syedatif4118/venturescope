"""Financial Modeling Agent - Validates projections and unit economics."""

from typing import Dict, Any, Optional, List
import logging
import re

from core.llm_client import HuggingFaceLLMClient

logger = logging.getLogger(__name__)


class FinancialModelingAgent:
    """Agent responsible for financial analysis and validation."""
    
    SYSTEM_PROMPT = """You are a financial analyst and CFO specializing in startup valuations.
Your role is to analyze financial projections, unit economics, and business model viability.

Focus on:
- Revenue projections and growth rates
- Unit economics (CAC, LTV, gross margins)
- Burn rate and runway
- Path to profitability
- Key financial assumptions
- Red flags in financial projections
- Realistic vs optimistic scenarios

Be skeptical of hockey stick projections. Look for realistic assumptions and sustainable unit economics."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        logger.info("Initialized FinancialModelingAgent")
    
    def process(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial projections and unit economics.
        
        Args:
            company_data: Data from previous agents
            
        Returns:
            Financial analysis results
        """
        company_name = company_data.get("enhanced_data", {}).get("company_name", "Unknown")
        logger.info(f"Analyzing financials for: {company_name}")
        
        # Extract financial data
        enhanced = company_data.get("enhanced_data", {})
        traction = enhanced.get("traction", "")
        business_model = enhanced.get("business_model", "")
        funding_ask = enhanced.get("funding_ask", "")
        tables = company_data.get("tables", [])
        
        # Parse financial metrics
        metrics = self._parse_financial_metrics(traction, tables)
        
        # LLM analysis
        analysis = self._generate_financial_analysis(
            company_name=company_name,
            traction=str(traction),
            business_model=str(business_model),
            funding_ask=str(funding_ask),
            metrics=metrics,
        )
        
        result = {
            "metrics": metrics,
            "analysis": analysis,
            "score": self._calculate_financial_score(analysis, metrics),
        }
        
        logger.info(f"Financial analysis complete. Score: {result['score']}/25")
        return result
    
    def _parse_financial_metrics(self, traction: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse financial metrics from traction data and tables.
        
        Args:
            traction: Traction text
            tables: Extracted tables from PDF
            
        Returns:
            Dictionary of financial metrics
        """
        metrics = {}
        
        # Convert traction to string if it's a dict
        traction_str = str(traction) if isinstance(traction, dict) else traction
        
        # Extract revenue
        revenue_patterns = [
            r'\$([\d,.]+[KMB]?)\s*(?:revenue|ARR|MRR)',
            r'revenue[:\s]*\$([\d,.]+[KMB]?)',
        ]
        for pattern in revenue_patterns:
            match = re.search(pattern, traction_str, re.IGNORECASE)
            if match:
                metrics['revenue'] = match.group(1)
                break
        
        # Extract users/customers
        user_patterns = [
            r'([\d,.]+[KMB]?)\s*(?:users|customers|clients)',
            r'(?:users|customers)[:\s]*([\d,.]+[KMB]?)',
        ]
        for pattern in user_patterns:
            match = re.search(pattern, traction_str, re.IGNORECASE)
            if match:
                metrics['users'] = match.group(1)
                break
        
        # Extract growth rate
        growth_match = re.search(r'(\d+)%\s*(?:growth|YoY|MoM)', traction_str, re.IGNORECASE)
        if growth_match:
            metrics['growth_rate'] = f"{growth_match.group(1)}%"
        
        # Try to extract from tables (if any)
        if tables and not metrics:
            # Look for financial tables
            for table in tables:
                table_data = table.get('data', [])
                if table_data:
                    # Simple heuristic: look for numeric data
                    for row in table_data:
                        if row and any('$' in str(cell) or 'revenue' in str(cell).lower() for cell in row):
                            metrics['has_financial_table'] = True
                            break
        
        return metrics
    
    def _generate_financial_analysis(
        self,
        company_name: str,
        traction: str,
        business_model: str,
        funding_ask: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate comprehensive financial analysis using LLM.
        
        Returns:
            Analysis with validation, assumptions, and score
        """
        metrics_summary = "\n".join([f"- {k}: {v}" for k, v in metrics.items()])
        
        prompt = f"""Analyze the financial viability of this startup:

Company: {company_name}

Business Model:
{business_model}

Traction/Metrics:
{traction}

Parsed Metrics:
{metrics_summary if metrics_summary else 'Limited financial data'}

Funding Ask: {funding_ask}

Provide analysis on:

1. Revenue Validation: Are the revenue/traction metrics credible? (2-3 sentences)
2. Unit Economics: What can we infer about unit economics and sustainability? (2-3 sentences)
3. Growth Assumptions: Are growth projections realistic? (2-3 sentences)
4. Financial Risks: What are the key financial risks? (2-3 sentences)
5. Financial Score: Rate the financial health and projections from 0-25 points.

Be realistic about early-stage startups, but flag any obvious red flags.
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1200,
                temperature=0.4,
            )
            
            return {
                "revenue_validation": self._extract_section(response, "Revenue Validation"),
                "unit_economics": self._extract_section(response, "Unit Economics"),
                "growth_assumptions": self._extract_section(response, "Growth Assumptions"),
                "financial_risks": self._extract_section(response, "Financial Risks"),
                "financial_score": self._extract_score(response),
                "full_analysis": response,
            }
        except Exception as e:
            logger.error(f"Error generating financial analysis: {str(e)}")
            return {
                "revenue_validation": "Unable to validate",
                "unit_economics": "Data unavailable",
                "growth_assumptions": "Unclear",
                "financial_risks": "Analysis failed",
                "financial_score": 15,
                "error": str(e),
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract specific section from LLM response."""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if section_name in line:
                for j in range(i+1, len(lines)):
                    if lines[j].strip() and not lines[j].strip().startswith(str(j)):
                        return lines[j].strip()
        return "Not specified"
    
    def _extract_score(self, text: str) -> int:
        """Extract financial score from LLM response."""
        import re
        match = re.search(r'(\d+)\s*(?:/25|points|out of 25)', text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 0), 25)
        return 15
    
    def _calculate_financial_score(self, analysis: Dict[str, Any], metrics: Dict[str, Any]) -> int:
        """Calculate final financial score.
        
        Returns:
            Score out of 25
        """
        base_score = analysis.get("financial_score", 15)
        
        # Adjust based on available metrics
        if metrics.get('revenue'):
            base_score = min(base_score + 3, 25)
        if metrics.get('growth_rate'):
            base_score = min(base_score + 2, 25)
        
        return base_score
