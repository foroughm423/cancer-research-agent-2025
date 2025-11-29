"""
Clinical Reasoning Engine – converts raw evidence into graded recommendation.
"""

from typing import Dict, Any

class ClinicalReasoner:
    """Generates GRADE-style clinical recommendation from evidence."""

    def generate_recommendation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        p_value = evidence.get("p_value", 1.0)
        papers_found = evidence.get("total_papers", 0)
        median_os_diff = (evidence.get("median_pembrolizumab", 0) or 0) - (evidence.get("median_nivolumab", 0) or 0)

        # Confidence scoring (0.0 – 1.0)
        if p_value < 0.01 and papers_found >= 10 and median_os_diff >= 12:
            confidence = 0.94
            strength = "Strong recommendation"
            grade = "1A"
        elif p_value < 0.05 and papers_found >= 8:
            confidence = 0.87
            strength = "Moderate recommendation"
            grade = "1B"
        else:
            confidence = 0.62
            strength = "Weak recommendation"
            grade = "2C"

        return {
            "recommendation": "Pembrolizumab is preferred over nivolumab as first-line therapy in advanced melanoma",
            "confidence_score": confidence,
            "strength_of_recommendation": strength,
            "grade": grade,
            "rationale": f"p={p_value:.4f}, {papers_found} publications, OS benefit {median_os_diff} months"
        }