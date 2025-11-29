"""
Doctor-in-the-Loop Agent
Simulates a senior oncologist who reviews, approves, modifies or rejects AI recommendations.
"""

import logging
from typing import Dict, Any, Literal

logger = logging.getLogger(__name__)

class DoctorAgent:
    """Human-in-the-loop oncologist agent with final decision authority."""

    def review_recommendation(self, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates physician review and approval workflow.
        In real deployment this would wait for actual human input.
        """
        logger.info("DoctorAgent reviewing AI-generated recommendation")

        # For demo: auto-approve with high confidence, but show realistic flow
        decision = "approve"  
        confidence = ai_output.get("confidence_score", 0.87)

        if confidence < 0.70:
            decision = "modify"
            comment = "Confidence too low. Recommend reducing pembrolizumab dose or adding corticosteroid prophylaxis."
        elif ai_output.get("p_value", 1.0) > 0.05:
            decision = "modify"
            comment = "Evidence not strong enough for first-line recommendation. Suggest clinical trial enrollment."
        else:
            decision = "approve"
            comment = "Strong evidence and acceptable safety profile. Proceed with recommendation."

        review = {
            "doctor_decision": decision,
            "doctor_name": "Dr. Sarah Johnson, MD – Medical Oncology",
            "timestamp": "2025-11-27 14:32",
            "confidence_score": round(confidence, 3),
            "comment": comment,
            "final_recommendation": ai_output["recommendation"] if decision == "approve" else comment
        }

        logger.info(f"Doctor decision: {decision.upper()}")
        return review