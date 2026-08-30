import pytest
from logassistant.schemas import ThreatReport
from pydantic import ValidationError


@pytest.fixture
def sample() -> ThreatReport:
    return ThreatReport(
        threat_type="Brute Force",
        severity="CRITICAL",
        mitigation_plan="Block ip 1.1.1.1",
        recommendations="Turn on firewall",
    )


def test_create_valid_report(sample):
    assert sample.threat_type == "Brute Force"
    assert sample.severity == "CRITICAL"
    assert sample.mitigation_plan == "Block ip 1.1.1.1"
    assert sample.recommendations == "Turn on firewall"


def test_missing_required_field_raises():
    with pytest.raises(ValidationError):
        ThreatReport(
            threat_type="Brute Force", severity="Critical", mitigation_plan="x"
        )  # pyright: ignore[reportCallIssue]


def test_wrong_type_for_threat_type():
    with pytest.raises(ValidationError):
        ThreatReport(
            threat_type=123,  # pyright: ignore[reportArgumentType]
            severity="Critical",  # pyright: ignore[reportArgumentType]
            mitigation_plan="x",
            recommendations="y",
        )


def test_severity_accepts_any_string_throw():
    with pytest.raises(ValueError):
        ThreatReport(
            threat_type="x",
            severity="banana",  # pyright: ignore[reportArgumentType]
            mitigation_plan="y",
            recommendations="z",
        )


def test_model_validate_from_llm_like_dict():
    data = {
        "threat_type": "SQL Injection",
        "severity": "HIGH",
        "mitigation_plan": "Sanitize inputs",
        "recommendations": "Use parameterized queries",
    }
    report = ThreatReport.model_validate(data)
    assert report.threat_type == "SQL Injection"
    assert report.severity == "HIGH"
    assert report.mitigation_plan == "Sanitize inputs"
    assert report.recommendations == "Use parameterized queries"


def test_extra_field_from_llm_output():
    data = {
        "threat_type": "SQL Injection",
        "severity": "HIGH",
        "mitigation_plan": "Sanitize inputs",
        "recommendations": "Use parameterized queries",
        "confidence": 0.95,
    }
    report = ThreatReport.model_validate(data)
    assert not hasattr(report, "confidence")


def test_serialization_round_trip(sample):
    dumped = sample.model_dump()
    restored = ThreatReport.model_validate(dumped)
    assert restored == sample


def test_severity_lowercase_gets_normalized():
    report = ThreatReport(
        threat_type="x",
        severity="critical",  # pyright: ignore[reportArgumentType]
        mitigation_plan="y",
        recommendations="z",
    )
    assert report.severity == "CRITICAL"


def test_severity_mixed_case_gets_normalized():
    report = ThreatReport(
        threat_type="x",
        severity="Critical",  # pyright: ignore[reportArgumentType]
        mitigation_plan="y",
        recommendations="z",
    )
    assert report.severity == "CRITICAL"


def test_severity_already_correct_case_unchanged():
    report = ThreatReport(
        threat_type="x", severity="CRITICAL", mitigation_plan="y", recommendations="z"
    )
    assert report.severity == "CRITICAL"
