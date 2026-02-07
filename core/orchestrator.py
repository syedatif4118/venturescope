"""
VentureScope Orchestrator - Coordinates all agents using LangGraph.
"""

from typing import Dict, Any, Optional
import logging
from pathlib import Path

from agents.document_ingestion import DocumentIngestionAgent
from agents.market_analysis import MarketAnalysisAgent
from agents.team_assessment import TeamAssessmentAgent
from agents.financial_modeling import FinancialModelingAgent
from agents.risk_flagging import RiskFlaggingAgent
from agents.memo_generator import MemoGeneratorAgent
from core.llm_client import HuggingFaceLLMClient
from core.enrichment_engine import EnrichmentEngine
from core.knowledge_store import KnowledgeStore
from core.fact_builder import InvestmentFactBuilder



logger = logging.getLogger(__name__)


class VentureScopeOrchestrator:
    """Orchestrates multi-agent analysis of pitch decks."""

    def __init__(self, llm_client: Optional[HuggingFaceLLMClient] = None):
        """
        Initialize orchestrator and all agents.
        """
        self.llm_client = llm_client or HuggingFaceLLMClient()

        self.document_agent = DocumentIngestionAgent(self.llm_client)
        self.market_agent = MarketAnalysisAgent(self.llm_client)
        self.team_agent = TeamAssessmentAgent(self.llm_client)
        self.financial_agent = FinancialModelingAgent(self.llm_client)
        self.risk_agent = RiskFlaggingAgent(self.llm_client)
        self.memo_agent = MemoGeneratorAgent(self.llm_client)
        self.enrichment_engine = EnrichmentEngine()
        self.knowledge_store = KnowledgeStore()
        self.fact_builder = InvestmentFactBuilder()



        logger.info("VentureScope Orchestrator initialized with all agents")

    # --------------------------------------------------
    # Main Pipeline
    # --------------------------------------------------

    def analyze_pitch_deck(self, pitch_deck_path: str) -> Dict[str, Any]:
        """
        Execute full analysis pipeline on a pitch deck.
        """

        logger.info(f"Starting analysis pipeline for: {pitch_deck_path}")

        if not Path(pitch_deck_path).exists():
            raise FileNotFoundError(
                f"Pitch deck not found: {pitch_deck_path}"
            )

        try:
            # Step 1: Document ingestion
            logger.info("Step 1/6: Document ingestion...")
            company_data = self.document_agent.process(pitch_deck_path)
            company_data = self.enrichment_engine.enrich(company_data)
            facts = self.fact_builder.build(company_data)



            # Step 2: Market analysis
            logger.info("Step 2/6: Market analysis...")
            market_analysis = self.market_agent.process(company_data)

            # Step 3: Team assessment
            logger.info("Step 3/6: Team assessment...")
            team_assessment = self.team_agent.process(company_data)

            # Step 4: Financial modeling
            logger.info("Step 4/6: Financial modeling...")
            financial_analysis = self.financial_agent.process(company_data)

            all_analyses = {
                "market": market_analysis,
                "team": team_assessment,
                "financial": financial_analysis,
            }

            # Step 5: Risk flagging
            logger.info("Step 5/6: Risk assessment...")
            risk_assessment = self.risk_agent.process(
                company_data,
                all_analyses
            )
            all_analyses["risk"] = risk_assessment

            # Final score
            final_score = self._calculate_final_score(all_analyses)

            # Step 6: Memo generation
            logger.info("Step 6/6: Generating investment memo...")
            memo_result = self.memo_agent.process(
                company_data=company_data,
                all_analyses=all_analyses,
                final_score=final_score,
            )
            deck_id = Path(pitch_deck_path).stem

            self.knowledge_store.save_structured(deck_id, company_data)
            self.knowledge_store.save_analysis(deck_id, all_analyses)
            self.knowledge_store.save_memo(deck_id, memo_result["memo"])


            result = {
                "company_name": company_data.get(
                    "enhanced_data", {}
                ).get("company_name", "Unknown"),
                "source_file": company_data.get("source_file", ""),
                "final_score": final_score,
                "recommendation": memo_result["recommendation"],
                "memo": memo_result["memo"],
                "analyses": {
                    "document": company_data,
                    "market": market_analysis,
                    "team": team_assessment,
                    "financial": financial_analysis,
                    "risk": risk_assessment,
                },
                "scores": {
                    "market": market_analysis.get("score", 0),
                    "team": team_assessment.get("score", 0),
                    "financial": financial_analysis.get("score", 0),
                    "total": final_score,
                },
                "generated_at": memo_result["generated_at"],
            }

            logger.info(
                f"Analysis complete! Score: {final_score}/100 | "
                f"Recommendation: {memo_result['recommendation']}"
            )

            return result

        except Exception as e:
            logger.error(
                f"Error in analysis pipeline: {str(e)}",
                exc_info=True
            )
            raise

    # --------------------------------------------------
    # Score Calculation
    # --------------------------------------------------

    def _calculate_final_score(self, analyses: Dict[str, Any]) -> int:

        market_score = analyses.get("market", {}).get("score", 0)
        team_score = analyses.get("team", {}).get("score", 0)
        financial_score = analyses.get("financial", {}).get("score", 0)

        risk_level = analyses.get("risk", {}).get(
            "risk_level", "MEDIUM"
        )

        execution_score = {
            "LOW": 25,
            "MEDIUM": 18,
            "HIGH": 12,
            "CRITICAL": 5,
        }.get(risk_level, 15)

        total_score = (
            market_score
            + team_score
            + financial_score
            + execution_score
        )

        return min(max(total_score, 0), 100)

    # --------------------------------------------------
    # Save Memo
    # --------------------------------------------------

    def save_memo(
        self,
        analysis_result: Dict[str, Any],
        output_dir: str = "outputs/investment_memos",
    ) -> str:

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        company_name = analysis_result["company_name"].replace(" ", "_")
        filepath = output_path / f"{company_name}_memo.md"

        with open(filepath, "w") as f:
            f.write(analysis_result["memo"])

        logger.info(f"Memo saved to: {filepath}")
        return str(filepath)
