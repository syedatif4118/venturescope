"""Document Ingestion Agent - Extracts structured data from pitch decks."""

from typing import Dict, Any, Optional
import logging
from pathlib import Path

from utils.pdf_extractor import PDFExtractor
from core.llm_client import HuggingFaceLLMClient

logger = logging.getLogger(__name__)


class DocumentIngestionAgent:
    """Agent responsible for extracting and structuring pitch deck data."""
    
    SYSTEM_PROMPT = """You are a document analysis expert specializing in startup pitch decks.
Your role is to extract and structure key information from pitch deck content.

Focus on identifying:
- Company name and tagline
- Problem statement
- Solution/product description
- Market size (TAM/SAM/SOM)
- Business model
- Traction and metrics
- Team information
- Funding ask
- Use of funds
- Competitors

Provide concise, factual summaries. If information is not found, indicate "Not specified"."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        logger.info("Initialized DocumentIngestionAgent")
    
    def process(self, pitch_deck_path: str) -> Dict[str, Any]:
        logger.info(f"Processing pitch deck: {pitch_deck_path}")

        extractor = PDFExtractor(pitch_deck_path)
        
        try:
            raw_data = extractor.extract_structured_data()
            tables = extractor.extract_tables()
            metadata = extractor.extract_metadata()

            enhanced_data = self._enhance_with_llm(raw_data)

            result = {
                "raw_data": raw_data,
                "enhanced_data": enhanced_data,
                "tables": tables,
                "metadata": metadata,
                "source_file": Path(pitch_deck_path).name,
            }

            logger.info(f"Successfully processed: {enhanced_data.get('company_name', 'Unknown')}")
            return result

        finally:
            extractor.close()           # Always clean up
    
    def _enhance_with_llm(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to enhance and validate extracted data.
        
        Args:
            raw_data: Raw extracted data from PDF
            
        Returns:
            Enhanced and validated data
        """
        full_text = raw_data.get("full_text", "")
        
        # If text is too long, truncate to first 8000 characters
        if len(full_text) > 8000:
            full_text = full_text[:8000] + "\n\n[Content truncated...]"
        
        prompt = f"""Analyze the following pitch deck content and extract key information:

{full_text}

Provide a structured analysis with the following:

1. Company Name:
2. Tagline (one sentence):
3. Problem Statement (2-3 sentences):
4. Solution (2-3 sentences):
5. Market Size (TAM/SAM/SOM if available):
6. Business Model:
7. Key Traction Metrics:
8. Team Highlights:
9. Funding Ask:
10. Competitors:

Be concise and factual. If information is not found, write "Not specified".
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for factual extraction
            )
            
            # Parse LLM response into structured format
            enhanced_data = self._parse_llm_response(response, raw_data)
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing data with LLM: {str(e)}")
            # Fall back to raw data
            return {
                "company_name": raw_data.get("company_name", "Unknown"),
                "tagline": raw_data.get("tagline", "Not specified"),
                "problem": raw_data.get("problem", "Not specified"),
                "solution": raw_data.get("solution", "Not specified"),
                "market_size": raw_data.get("market_size", {}),
                "business_model": raw_data.get("business_model", "Not specified"),
                "traction": raw_data.get("traction", {}),
                "team": raw_data.get("team", "Not specified"),
                "funding_ask": raw_data.get("funding_ask", "Not specified"),
                "competitors": raw_data.get("competitors", []),
                "error": str(e),
            }
    
    def _parse_llm_response(self, response: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured dictionary.
        
        Args:
            response: LLM generated response
            raw_data: Original raw data for fallback
            
        Returns:
            Structured dictionary
        """
        lines = response.strip().split('\n')
        data = {}
        
        # Simple parsing logic
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Map keys
                if 'company_name' in key or key.startswith('1'):
                    data['company_name'] = value
                elif 'tagline' in key or key.startswith('2'):
                    data['tagline'] = value
                elif 'problem' in key or key.startswith('3'):
                    data['problem'] = value
                elif 'solution' in key or key.startswith('4'):
                    data['solution'] = value
                elif 'market' in key or key.startswith('5'):
                    data['market_size'] = value
                elif 'business' in key or 'model' in key or key.startswith('6'):
                    data['business_model'] = value
                elif 'traction' in key or 'metrics' in key or key.startswith('7'):
                    data['traction'] = value
                elif 'team' in key or key.startswith('8'):
                    data['team'] = value
                elif 'funding' in key or 'ask' in key or key.startswith('9'):
                    data['funding_ask'] = value
                elif 'competitor' in key or key.startswith('10'):
                    data['competitors'] = value
        
        # Fallback to raw data if parsing failed
        return {
            "company_name": data.get('company_name') or raw_data.get('company_name', 'Unknown'),
            "tagline": data.get('tagline', 'Not specified'),
            "problem": data.get('problem', 'Not specified'),
            "solution": data.get('solution', 'Not specified'),
            "market_size": data.get('market_size') or raw_data.get('market_size', 'Not specified'),
            "business_model": data.get('business_model', 'Not specified'),
            "traction": data.get('traction') or raw_data.get('traction', 'Not specified'),
            "team": data.get('team', 'Not specified'),
            "funding_ask": data.get('funding_ask') or raw_data.get('funding_ask', 'Not specified'),
            "competitors": data.get('competitors') or raw_data.get('competitors', 'Not specified'),
        }
