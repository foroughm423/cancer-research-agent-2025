"""
Statistical Analysis Agent for oncology survival data.
Responsible for Kaplan-Meier estimation and log-rank testing.
"""

import logging
from typing import Dict, Any
from tools.stats_tool import perform_survival_analysis

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """
    Specialized agent for statistical survival analysis in clinical research.
    Does NOT print anything — only returns formatted text for the supervisor.
    """

    def __init__(self) -> None:
        logger.info("AnalysisAgent initialized")

    def analyze_survival(self) -> Dict[str, Any]:
        """
        Execute survival analysis using simulated clinical trial data.
        
        Returns:
            Dictionary containing results and a clean formatted summary string.
        """
        result = perform_survival_analysis()
        
        if result["status"] != "success":
            return {
                "status": "error",
                "message": result.get("error", "Unknown analysis error")
            }

        # Create clean, formatted summary — NO print statements here
        summary = (
            "\nSURVIVAL ANALYSIS RESULTS\n"
            + "=" * 70 + "\n"
            + f"Comparison        : Pembrolizumab vs Nivolumab\n"
            + f"Statistical test  : Log-rank test\n"
            + f"P-value           : {result['p_value']}\n"
            + f"Test statistic    : {result['test_statistic']}\n"
            + f"Median OS (Pembro): {result['median_pembrolizumab'] or 'N/A'} months\n"
            + f"Median OS (Nivo)  : {result['median_nivolumab'] or 'N/A'} months\n"
            + "\nInterpretation:\n"
            + f"{result['interpretation']}\n"
            + f"\nFigure saved at: {result['figure_path']}\n"
            + "=" * 70
        )

        return {
            "status": "success",
            "summary": summary,
            "figure_path": result["figure_path"],
            "p_value": result["p_value"],
            "median_pembrolizumab": result["median_pembrolizumab"],
            "median_nivolumab": result["median_nivolumab"]
        }

    def get_agent(self):
        return self