"""
Oncology Research Supervisor with full clinical decision support workflow.
Integrates literature review, survival analysis, clinical reasoning, and physician oversight.
"""

import logging
from typing import Dict, Any
from agents.literature_agent import LiteratureAgent
from agents.analysis_agent import AnalysisAgent
from agents.doctor_agent import DoctorAgent
from agents.clinical_reasoner import ClinicalReasoner
from tools.risk_calculator import calculate_irae_risk

logger = logging.getLogger(__name__)


class OncologySupervisor:
    """
    Central coordinator for the complete oncology research and clinical decision workflow.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        self.literature_agent = LiteratureAgent(model_name=model_name)
        self.analysis_agent = AnalysisAgent()
        self.clinical_reasoner = ClinicalReasoner()
        self.doctor_agent = DoctorAgent()
        logger.info("OncologySupervisor initialized with full clinical workflow agents")

    def process_query(self, query: str) -> Dict[str, Any]:
        logger.info("Starting clinical research workflow for query: %s", query)

        # 1. Literature search
        lit_result = self.literature_agent.query(query)
        if lit_result.get("status") == "success":
            self._format_literature_output(lit_result)

        # 2. Survival analysis
        print("\n" + "═" * 70)
        print("STATISTICAL SURVIVAL ANALYSIS")
        print("═" * 70)
        analysis_result = self.analysis_agent.analyze_survival()
        if analysis_result["status"] == "success":
            print(analysis_result["summary"])

        # 3. Clinical reasoning
        evidence = {
            "p_value": analysis_result.get("p_value", 1.0),
            "total_papers": lit_result.get("total_found", 0),
            "median_pembrolizumab": analysis_result.get("median_pembrolizumab"),
            "median_nivolumab": analysis_result.get("median_nivolumab")
        }
        recommendation = self.clinical_reasoner.generate_recommendation(evidence)

        # 4. Physician review
        doctor_review = self.doctor_agent.review_recommendation({
            "recommendation": recommendation["recommendation"],
            "confidence_score": recommendation["confidence_score"],
            "p_value": evidence["p_value"]
        })

        # 5. Risk profile
        risk_profile = calculate_irae_risk()

        # 6. Final report
        self._display_clinical_report(recommendation, doctor_review, risk_profile)

        return {
            "literature": lit_result,
            "analysis": analysis_result,
            "recommendation": recommendation,
            "doctor_review": doctor_review,
            "risk_profile": risk_profile
        }

    def _format_literature_output(self, result: Dict[str, Any]) -> None:
        print("\n" + "═" * 70)
        print("LITERATURE SEARCH RESULTS")
        print("═" * 70)
        print(f"\nQuery          : {result['query']}")
        print(f"Total papers   : {result['total_found']}")
        print(f"Sources        : PubMed ({result.get('pubmed_count', 0)}), "
              f"Google Scholar ({result.get('scholar_count', 0)})")
        print("\n" + "-" * 70)
        print("TOP PUBLICATIONS")
        print("-" * 70)
        for i, paper in enumerate(result["papers"][:6], 1):
            src = paper.get("source", "Unknown")
            year = paper.get("year", "N/A")
            print(f"\n[{i}] {paper['title']}")
            print(f"    Source: {src} | Year: {year}")
            if src == "PubMed":
                authors = ", ".join(paper.get("authors", ["Unknown"])[:3])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                print(f"    Authors: {authors}")
                print(f"    Journal: {paper.get('journal', 'N/A')} | PMID: {paper.get('pmid', 'N/A')}")
        print("\n" + "-" * 70)
        print("SEARCH SUMMARY")
        print("-" * 70)
        print(result.get("analysis", "No summary available"))
        print()

    def _display_clinical_report(
        self,
        recommendation: Dict[str, Any],
        doctor_review: Dict[str, Any],
        risk_profile: Dict[str, Any]
    ) -> None:
        print("\n" + "═" * 70)
        print("CLINICAL DECISION SUPPORT REPORT")
        print("═" * 70)
        print(f"\nRecommendation      : {doctor_review['final_recommendation']}")
        print(f"Strength            : {recommendation['strength_of_recommendation']} "
              f"(GRADE {recommendation['grade']})")
        print(f"Confidence Score    : {recommendation['confidence_score']:.1%}")
        print(f"Rationale           : {recommendation['rationale']}")
        print(f"\nPhysician Review    : {doctor_review['doctor_decision'].upper()}")
        print(f"Reviewing Physician : {doctor_review['doctor_name']}")
        print(f"Comment             : {doctor_review['comment']}")
        print(f"\nAdverse Event Risk  : Grade 3–4 irAE: {risk_profile['grade_3_4_irae']}")
        print(f"Monitoring Advice   : {risk_profile['recommendation']}")
        print("═" * 70)

    def get_agent(self):
        return self