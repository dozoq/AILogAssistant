from pydantic import BaseModel, Field

class ThreatReport(BaseModel):
    threat_type: str = Field(..., description="Type of security threat")
    severity: str = Field(..., description="Severity level of the threat (LOW/MEDIUM/HIGH/CRITICAL)")
    mitigation_plan: str = Field(..., description="Steps to mitigate the threat")
    recommendations: str = Field(..., description="Additional recommendations for improving security")