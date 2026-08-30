from pydantic import BaseModel, Field

from logassistant.schemas.detection_rule import DetectionRule


class GlobalSecurityPolicy(BaseModel):
    rules: list[DetectionRule] = Field(..., description="deteciton rules list")
