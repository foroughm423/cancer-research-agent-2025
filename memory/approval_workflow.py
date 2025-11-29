"""
Tracks human approval status in long-term memory.
"""

import logging
from memory.memory_service import OncologyMemoryService

logger = logging.getLogger(__name__)
memory = OncologyMemoryService()

def log_doctor_approval(session_id: str, decision: str, doctor: str):
    memory.save_doctor_review(
        session_id=session_id,
        decision=decision,
        doctor_name=doctor,
        comment="Approved via Doctor-in-the-Loop system"
    )
    logger.info(f"Doctor approval logged for session {session_id}")