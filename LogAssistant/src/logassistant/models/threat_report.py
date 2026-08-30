from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from logassistant.core.database import Base


class ThreatReport(Base):
    __tablename__ = "threat_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    threat_type: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(255))
    mitigation_plan: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[str] = mapped_column(Text)
