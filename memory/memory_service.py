"""
Long-term memory service for the Oncology Research Agent.
Stores research sessions, findings, and physician review decisions.
"""

import os
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Database setup
# ----------------------------------------------------------------------
BASE = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///memory/cancer_research.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


class ResearchMemory(BASE):
    __tablename__ = "research_memory"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    query = Column(Text, nullable=False)
    cancer_type = Column(String(100), nullable=False)
    findings = Column(Text)                     # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ResearchMemory {self.session_id} – {self.cancer_type}>"


# Create tables if they don't exist
BASE.metadata.create_all(engine)


# ----------------------------------------------------------------------
# Memory Service
# ----------------------------------------------------------------------
class OncologyMemoryService:
    """
    Persistent memory service for research sessions and physician approvals.
    """

    def __init__(self) -> None:
        self.session = Session()
        logger.info(f"Memory service initialized: {DATABASE_URL}")

    # ------------------------------------------------------------------
    # Save a full research session
    # ------------------------------------------------------------------
    def save_research(
        self,
        session_id: str,
        query: str,
        cancer_type: str,
        findings: Dict[str, Any]
    ) -> int:
        """
        Persist a research session and its findings.

        Returns:
            Database record ID
        """
        try:
            entry = ResearchMemory(
                session_id=session_id,
                query=query,
                cancer_type=cancer_type,
                findings=json.dumps(findings, ensure_ascii=False),
                timestamp=datetime.utcnow()
            )
            self.session.add(entry)
            self.session.commit()
            logger.info(f"Research session saved – ID {entry.id}")
            return entry.id
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save research session: {e}")
            raise

    # ------------------------------------------------------------------
    # Save physician review decision (Doctor-in-the-Loop)
    # ------------------------------------------------------------------
    def save_doctor_review(
        self,
        session_id: str,
        decision: str,
        doctor_name: str,
        comment: str = ""
    ) -> int:
        """
        Record physician review decision in long-term memory.

        Args:
            session_id: Identifier linking to the original research session
            decision: "approve", "modify", or "reject"
            doctor_name: Full name and title of the reviewing physician
            comment: Optional clinical comment

        Returns:
            Database record ID
        """
        try:
            record = {
                "decision": decision,
                "doctor": doctor_name,
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat()
            }

            entry = ResearchMemory(
                session_id=session_id,
                query="Physician Review",
                cancer_type="clinical_decision",
                findings=json.dumps(record, ensure_ascii=False),
                timestamp=datetime.utcnow()
            )
            self.session.add(entry)
            self.session.commit()
            logger.info(f"Physician review saved – Decision: {decision} (ID {entry.id})")
            return entry.id

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save physician review: {e}")
            raise

    # ------------------------------------------------------------------
    # Optional: retrieve past sessions (useful for audit)
    # ------------------------------------------------------------------
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        entry = self.session.query(ResearchMemory).filter_by(session_id=session_id).first()
        if entry:
            return {
                "id": entry.id,
                "query": entry.query,
                "cancer_type": entry.cancer_type,
                "findings": json.loads(entry.findings) if entry.findings else {},
                "timestamp": entry.timestamp
            }
        return None

    def close(self) -> None:
        self.session.close()