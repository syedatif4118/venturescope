"""Team Assessment Agent - Evaluates founder backgrounds and team composition."""

from typing import Dict, Any, List, Optional
import logging
import re

from core.llm_client import HuggingFaceLLMClient
from utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class TeamAssessmentAgent:
    """Agent responsible for evaluating founding team quality and experience."""
    
    SYSTEM_PROMPT = """You are an executive recruiter and venture capitalist specializing in team assessment.
Your role is to evaluate founding teams for startups, focusing on:

- Founder backgrounds and relevant experience
- Technical capabilities
- Domain expertise
- Previous exits or notable achievements
- Team composition and skill balance
- Gaps in the team
- Coachability indicators

Provide honest, constructive assessments. Great teams can overcome weak ideas, but weak teams rarely succeed."""
    
    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        self.llm_client = llm_client or HuggingFaceLLMClient()
        self.web_scraper = WebScraper()
        logger.info("Initialized TeamAssessmentAgent")
    
    def process(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess founding team quality and experience.
        
        Args:
            company_data: Data from previous agents
            
        Returns:
            Team assessment results
        """
        company_name = company_data.get("enhanced_data", {}).get("company_name", "Unknown")
        logger.info(f"Assessing team for: {company_name}")
        
        # Extract team info
        team_info = company_data.get("enhanced_data", {}).get("team", "")
        
        # Parse team members
        team_members = self._parse_team_members(team_info)
        
        # Research founders
        founder_research = []
        for member in team_members[:3]:  # Research top 3 founders
            research = self.web_scraper.search_founder(member.get("name", ""))
            founder_research.append(research)
        
        # LLM assessment
        assessment = self._generate_team_assessment(
            company_name=company_name,
            team_info=team_info,
            team_members=team_members,
            founder_research=founder_research,
        )
        
        result = {
            "team_members": team_members,
            "founder_research": founder_research,
            "assessment": assessment,
            "score": self._calculate_team_score(assessment, team_members),
        }
        
        logger.info(f"Team assessment complete. Score: {result['score']}/25")
        return result
    
    def _parse_team_members(self, team_info: str) -> List[Dict[str, Any]]:
        """Parse team member information from text.
        
        Args:
            team_info: Team section text
            
        Returns:
            List of team member dictionaries
        """
        members = []
        
        if not team_info or team_info == "Not specified":
            return members
        
        # Look for patterns like "John Doe - CEO" or "Jane Smith, CTO"
        patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[-,:]\s*(CEO|CTO|CFO|COO|Founder|Co-founder)',
            r'(CEO|CTO|CFO|COO|Founder):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, team_info, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    name, role = match if match[0][0].isupper() else (match[1], match[0])
                    members.append({
                        "name": name.strip(),
                        "role": role.strip(),
                    })
        
        # If no structured parsing worked, extract capitalized names
        if not members:
            names = re.findall(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', team_info)
            for name in names[:5]:  # Max 5 names
                if name not in ["Not Specified", "The Team"]:
                    members.append({
                        "name": name,
                        "role": "Team Member",
                    })
        
        return members
    
    def _generate_team_assessment(
        self,
        company_name: str,
        team_info: str,
        team_members: List[Dict[str, Any]],
        founder_research: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate comprehensive team assessment using LLM.
        
        Returns:
            Assessment with strengths, weaknesses, and score
        """
        # Summarize research
        research_summary = "\n".join([
            f"- {r.get('name', 'Unknown')}: {r.get('summary', 'No data')[:200]}"
            for r in founder_research
        ])
        
        prompt = f"""Assess the founding team for this startup:

Company: {company_name}

Team Information:
{team_info}

Team Members Identified:
{', '.join([f"{m['name']} ({m['role']})" for m in team_members])}

Founder Research:
{research_summary if research_summary else 'Limited public information available'}

Provide assessment on:

1. Team Strengths: What are the key strengths of this team? (2-3 sentences)
2. Experience Relevance: How relevant is their experience to this venture? (2-3 sentences)
3. Team Gaps: What critical gaps exist in skills/experience? (2-3 sentences)
4. Execution Capability: Can this team execute on the vision? (2-3 sentences)
5. Team Score: Rate the team from 0-25 points based on experience, composition, and execution capability.

Be honest and constructive in your assessment.
"""
        
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                max_tokens=1200,
                temperature=0.4,
            )
            
            return {
                "team_strengths": self._extract_section(response, "Team Strengths"),
                "experience_relevance": self._extract_section(response, "Experience Relevance"),
                "team_gaps": self._extract_section(response, "Team Gaps"),
                "execution_capability": self._extract_section(response, "Execution Capability"),
                "team_score": self._extract_score(response),
                "full_assessment": response,
            }
        except Exception as e:
            logger.error(f"Error generating team assessment: {str(e)}")
            return {
                "team_strengths": "Unable to assess",
                "experience_relevance": "Data unavailable",
                "team_gaps": "Unclear",
                "execution_capability": "Unknown",
                "team_score": 15,  # Default middle score
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
        """Extract team score from LLM response."""
        import re
        match = re.search(r'(\d+)\s*(?:/25|points|out of 25)', text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return min(max(score, 0), 25)
        return 15
    
    def _calculate_team_score(self, assessment: Dict[str, Any], team_members: List[Dict[str, Any]]) -> int:
        """Calculate final team score.
        
        Returns:
            Score out of 25
        """
        base_score = assessment.get("team_score", 15)
        
        # Adjust based on team size
        if len(team_members) == 0:
            base_score = max(base_score - 5, 0)
        elif len(team_members) >= 3:
            base_score = min(base_score + 2, 25)
        
        return base_score
