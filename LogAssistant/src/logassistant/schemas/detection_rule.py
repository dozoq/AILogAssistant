import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DetectionRule(BaseModel):
    name: str = Field(..., description="Unique security rule name")
    pattern: str = Field(..., description="Raw rule regex pattern")
    target_field: str = Field(default="url", description="targeted field")
    on_success_score: int = Field(
        ..., description="Risk ranking score on succesful attack try"
    )
    on_reject_score: int = Field(..., description="Risk ranging score on rejection")
    type: str = Field(..., description="rule type")
    volumetric_threshold: int | None = Field(default=None, description="threshold")
    compiled_regex: re.Pattern | None = Field(default=None, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("volumetric_threshold")
    @classmethod
    def check_volumetric_threshold(cls, v: Optional[int], info) -> Optional[int]:
        if info.data.get("type") == "volumetric" and v is None:
            raise ValueError("needed field")
        return v
