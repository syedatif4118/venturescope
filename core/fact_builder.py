"""
Build structured investment facts from extracted data.
"""

from typing import Dict, Any


class InvestmentFactBuilder:

    def build(self, company_data: Dict[str, Any]) -> Dict[str, Any]:

        facts = {
            "company": company_data.get("company_name"),
            "traction_present": bool(company_data.get("traction")),
            "market_defined": bool(company_data.get("market_size")),
            "text_length": len(company_data.get("full_text", "")),
            "extraction_quality": company_data.get("extraction_quality"),
        }

        return facts
