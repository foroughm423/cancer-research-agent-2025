"""
Enhanced Literature Search Agent with dual-source retrieval.
Combines PubMed (clinical) and Google Scholar (academic) sources.
"""

import os
import logging
from typing import Dict, Any, List
from tools.pubmed_tool import search_pubmed
from tools.scholar_tool import search_scholar

logger = logging.getLogger(__name__)


class LiteratureAgent:
    """
    Literature search agent with multi-source capability.
    Primary: PubMed for clinical trials and medical literature
    Secondary: Google Scholar for broader academic coverage
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.model_name = model_name
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        
        logger.info("LiteratureAgent initialized with PubMed + Google Scholar integration")

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Execute multi-source literature search.
        
        Args:
            user_query: Research query string
            
        Returns:
            Aggregated results from PubMed and Scholar
        """
        try:
            logger.info("Executing dual-source search: %s", user_query)

            # Search PubMed (primary clinical source)
            pubmed_result = search_pubmed(
                query=user_query,
                max_results=12,
                min_year=2023
            )
            
            # Search Google Scholar (supplementary academic source)
            scholar_result = search_scholar(
                query=user_query,
                max_results=6
            )

            # Aggregate results
            pubmed_papers = (
                pubmed_result.get("papers", [])
                if pubmed_result.get("status") == "success"
                else []
            )
            
            scholar_papers = (
                scholar_result.get("papers", [])
                if scholar_result.get("status") == "success"
                else []
            )

            # Tag sources
            all_papers = (
                [{"source": "PubMed", **p} for p in pubmed_papers] +
                scholar_papers
            )

            summary = self._generate_summary(len(pubmed_papers), len(scholar_papers))

            return {
                "status": "success",
                "query": user_query,
                "total_found": len(all_papers),
                "papers": all_papers[:20],
                "sources_used": ["PubMed", "Google Scholar"],
                "pubmed_count": len(pubmed_papers),
                "scholar_count": len(scholar_papers),
                "model_used": self.model_name,
                "analysis": summary
            }

        except Exception as exc:
            logger.error("Literature search failed: %s", exc)
            return {
                "status": "error",
                "error": str(exc),
                "query": user_query
            }

    def _generate_summary(self, pubmed_count: int, scholar_count: int) -> str:
        """Generate search summary text."""
        parts = []
        
        if pubmed_count > 0:
            parts.append(f"{pubmed_count} publications from PubMed")
        
        if scholar_count > 0:
            parts.append(f"{scholar_count} from Google Scholar")
        
        if not parts:
            return "No publications found matching the query criteria."
        
        return (
            f"Retrieved {' and '.join(parts)} covering recent advances "
            f"in the specified research area (2023-2025)."
        )

    def get_agent(self):
        return self


# Test
if __name__ == "__main__":
    print("Testing enhanced Literature Agent\n")
    
    agent = LiteratureAgent()
    result = agent.query("pembrolizumab melanoma 2024")
    
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Total papers: {result['total_found']}")
        print(f"PubMed: {result['pubmed_count']}, Scholar: {result['scholar_count']}")
        print(f"\nAnalysis: {result['analysis']}")