import pytest
from logassistant.core import BussinessException
from logassistant.models import ThreatReport
from logassistant.schemas import ThreatReport as ThreatReportDTO
from logassistant.services import ThreatService


@pytest.fixture
async def existing_report(threat_service: ThreatService) -> ThreatReport:
    new_report = ThreatReportDTO(
        threat_type="Brute Force",
        severity="CRITICAL",
        mitigation_plan="Block ip 1.1.1.1",
        recommendations="Turn on firewall",
    )
    return await threat_service.create_new_report(new_report)


@pytest.mark.anyio
async def test_create_new_report_saves_to_db(threat_service: ThreatService):
    new_report = ThreatReportDTO(
        threat_type="Brute Force",
        severity="CRITICAL",
        mitigation_plan="Block ip 1.1.1.1",
        recommendations="Turn on firewall",
    )

    saved_report = await threat_service.create_new_report(new_report)

    assert saved_report.id is not None
    assert (
        saved_report.threat_type,
        saved_report.severity,
        saved_report.mitigation_plan,
        saved_report.recommendations,
    ) == (
        new_report.threat_type,
        new_report.severity,
        new_report.mitigation_plan,
        new_report.recommendations,
    )


@pytest.mark.anyio
async def test_get_one_report_success(
    threat_service: ThreatService, existing_report: ThreatReport
):
    result = await threat_service.get_threat_report(existing_report.id)
    assert result.id == existing_report.id
    assert result.threat_type == existing_report.threat_type


@pytest.mark.anyio
async def test_get_does_not_exist_report_throw_exception(threat_service: ThreatService):
    with pytest.raises(BussinessException):
        await threat_service.get_threat_report(1)


@pytest.mark.anyio
async def test_get_all_reports_return_existing_report(
    threat_service: ThreatService, existing_report: ThreatReport
):
    result = await threat_service.get_threat_reports()
    assert existing_report in result
    assert len(result) == 1


@pytest.mark.anyio
async def test_delete_report_success(
    threat_service: ThreatService, existing_report: ThreatReport
):
    await threat_service.delete_threat_report(existing_report.id)
    result = await threat_service.get_threat_reports()
    assert existing_report not in result
    assert len(result) == 0


@pytest.mark.anyio
async def test_delete_does_not_exist_report_throw_exception(
    threat_service: ThreatService,
):
    with pytest.raises(BussinessException):
        await threat_service.delete_threat_report(1)
