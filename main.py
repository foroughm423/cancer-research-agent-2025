"""
Oncology Research Agent
Multi-agent clinical decision support system with physician-in-the-loop validation.
"""

import os
import logging
from dotenv import load_dotenv
from agents.supervisor import OncologySupervisor
from memory.memory_service import OncologyMemoryService
from memory.approval_workflow import log_doctor_approval

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    print("═" * 78)
    print("ONCOLOGY RESEARCH AGENT – Clinical Decision Support System")
    print("═" * 78)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "your_api_key" in api_key.lower():
        print("ERROR: Please configure a valid GOOGLE_API_KEY in the .env file.")
        return

    logger.info("API key validated")

    supervisor = OncologySupervisor(model_name="gemini-2.5-flash")
    query = "pembrolizumab AND melanoma AND (2024/01/01:2025/12/31[PDAT])"

    print(f"\nInitiating clinical evidence review: {query}\n")

    try:
        result = supervisor.process_query(query)

        # Log physician decision if approved
        if result["doctor_review"]["doctor_decision"] == "approve":
            log_doctor_approval(
                session_id="melanoma_clinical_review_2025",
                decision="approved",
                doctor=result["doctor_review"]["doctor_name"]
            )

        # Save full session
        OncologyMemoryService().save_research(
            session_id="melanoma_workflow_2025",
            query=query,
            cancer_type="melanoma",
            findings={
                "total_papers": result["literature"].get("total_found"),
                "p_value": result["analysis"].get("p_value"),
                "grade": result["recommendation"]["grade"],
                "physician_decision": result["doctor_review"]["doctor_decision"],
                "confidence": result["recommendation"]["confidence_score"]
            }
        )

        logger.info("Clinical workflow completed and archived")

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        print(f"Error: {e}")

    print("\nClinical decision support process completed.\n")


if __name__ == "__main__":
    main()