from pydantic import BaseModel, Field

class AIThreatReport(BaseModel):
    threat_type: str = Field(..., alias="threat_type")
    severity: str
    mitigation_plan: str
    recommendations: str

class WebSocketAlert(BaseModel):
    attacker_ip: str = Field(..., alias="ip")
    raw_details: str = Field(..., alias="details")
    ai_report: AIThreatReport

    class Config:
        populate_by_name = True 