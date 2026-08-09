from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator

class DetectionRule(BaseModel):
    name: str = Field(..., description="Unique security rule name")
    pattern: str = Field(..., description="Raw rule regex pattern")
    target_field: str = Field(default="url", description="targeted field")
    on_success_score: int = Field(..., description="Risk ranking score on succesful attack try")
    on_reject_score: int = Field(..., description="Risk ranging score on rejection")
    type: str = Field(..., description="rule type")
    volumetric_threshold: Optional[int] = Field(default=None, description="threshold")
    compiled_regex: Optional[re.Pattern] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed  = True

    @field_validator("volumetric_threshold")
    @classmethod
    def check_volumetric_threshold(cls, v: Optional[int],info) -> Optional[int]:
        if info.data.get("type") == "volumetric" and v is None:
            raise ValueError("needed field")
        return v