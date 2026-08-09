from pydantic import BaseModel,Field
from typing import List
from logassistant.models.detection_rule import DetectionRule
class GlobalSecurityPolicy(BaseModel):
    rules: List[DetectionRule] = Field(...,description="deteciton rules list")