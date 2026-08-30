from typing import Literal

from langchain_core.tools import tool


@tool
def submit_threat_report(
    threat_type: str,
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    mitigation_plan: str,
    recommendations: str,
) -> str:
    """Call this exactly once, when your investigation is complete, to submit the final structured threat report."""
    return "Report submitted."
