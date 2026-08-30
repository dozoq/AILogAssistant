from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from logassistant.core import BussinessException
from logassistant.models import ThreatReport
from logassistant.schemas import ThreatReport as ThreatReportDTO


class ThreatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_new_report(self, new_report: ThreatReportDTO) -> ThreatReport:
        threat_model = ThreatReport(**new_report.model_dump())
        self.db.add(threat_model)
        await self.db.commit()
        await self.db.refresh(threat_model)
        return threat_model

    async def get_threat_reports(self) -> list[ThreatReport]:
        query = select(ThreatReport)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_threat_report(self, id: int) -> ThreatReport:
        query = select(ThreatReport).where(ThreatReport.id == id)
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()
        if not report:
            raise BussinessException("Invalid Get")
        return report

    async def delete_threat_report(self, id: int) -> None:
        query = delete(ThreatReport).where(ThreatReport.id == id)
        result = await self.db.execute(query)
        if result.rowcount != 1:
            raise BussinessException("Invalid Delete")
        await self.db.commit()
