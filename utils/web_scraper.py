"""Web Scraping Utilities for Market Research."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import logging
import time
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape web for company info, competitors, market data."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
    
    def search_company(self, company_name: str) -> Dict[str, Any]:
        """Search for company information.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with company info
        """
        try:
            # Search DuckDuckGo (no API key needed)
            query = f"{company_name} startup company"
            results = self._duckduckgo_search(query, max_results=3)
            
            return {
                "company_name": company_name,
                "search_results": results,
                "summary": self._extract_summary(results),
            }
        except Exception as e:
            logger.error(f"Error searching for company {company_name}: {str(e)}")
            return {"company_name": company_name, "error": str(e)}
    
    def search_competitors(self, company_name: str, industry: str) -> List[Dict[str, str]]:
        """Search for competitors in the same industry.
        
        Args:
            company_name: Name of the company
            industry: Industry/sector
            
        Returns:
            List of competitor information
        """
        try:
            query = f"{company_name} competitors {industry}"
            results = self._duckduckgo_search(query, max_results=5)
            
            competitors = []
            for result in results:
                competitors.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("url", ""),
                })
            
            return competitors
        except Exception as e:
            logger.error(f"Error searching competitors: {str(e)}")
            return []
    
    def search_market_size(self, industry: str, market: str = "global") -> Dict[str, Any]:
        """Search for market size information.
        
        Args:
            industry: Industry/sector
            market: Geographic market (default: global)
            
        Returns:
            Market size data
        """
        try:
            query = f"{industry} market size {market} TAM SAM"
            results = self._duckduckgo_search(query, max_results=3)
            
            return {
                "industry": industry,
                "market": market,
                "sources": results,
                "summary": self._extract_market_summary(results),
            }
        except Exception as e:
            logger.error(f"Error searching market size: {str(e)}")
            return {"industry": industry, "error": str(e)}
    
    def search_founder(self, founder_name: str) -> Dict[str, Any]:
        """Search for founder information.
        
        Args:
            founder_name: Name of the founder
            
        Returns:
            Founder background info
        """
        try:
            # Search for LinkedIn profile (without API)
            query = f"{founder_name} founder CEO LinkedIn"
            results = self._duckduckgo_search(query, max_results=3)
            
            return {
                "name": founder_name,
                "search_results": results,
                "summary": self._extract_summary(results),
            }
        except Exception as e:
            logger.error(f"Error searching founder {founder_name}: {str(e)}")
            return {"name": founder_name, "error": str(e)}
    
    def _duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search DuckDuckGo (no API key required).
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get('href', ''),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                    })
            
            time.sleep(1)  # Be respectful with rate limiting
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _extract_summary(self, results: List[Dict[str, str]]) -> str:
        """Extract summary from search results."""
        summaries = [r.get("snippet", "") for r in results if r.get("snippet")]
        return " ".join(summaries[:3])  # First 3 snippets
    
    def _extract_market_summary(self, results: List[Dict[str, str]]) -> str:
        """Extract market size summary from results."""
        # Look for market size mentions in snippets
        summary = ""
        for result in results:
            snippet = result.get("snippet", "")
            # Look for patterns like "$XB market", "valued at $X"
            if "$" in snippet or "billion" in snippet.lower() or "market" in snippet.lower():
                summary += snippet + " "
        return summary.strip()
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Get full page content from URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Page text content
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error getting page content from {url}: {str(e)}")
            return None
