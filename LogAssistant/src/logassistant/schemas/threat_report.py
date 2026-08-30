from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ThreatReport(BaseModel):
    threat_type: str = Field(..., description="Type of security threat")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="Severity level of the threat (LOW/MEDIUM/HIGH/CRITICAL)"
    )
    mitigation_plan: str = Field(..., description="Steps to mitigate the threat")
    recommendations: str = Field(
        ..., description="Additional recommendations for improving security"
    )

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value):
        if isinstance(value, str):
            return value.upper()
        return value
