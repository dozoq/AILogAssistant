from typing import Annotated

from fastapi import Depends
from logassistant.api.dependencies import DatabaseDependency
from logassistant.domain import PolicyEngine
from logassistant.schemas.global_security_policy import GlobalSecurityPolicy
from logassistant.services import FileHandler, LogService, ThreatService


def get_threat_service(db: DatabaseDependency) -> ThreatService:
    return ThreatService(db)


threat_service_dependency = Annotated[ThreatService, Depends(get_threat_service)]


async def get_log_service() -> LogService:
    config_data = await FileHandler.load_policies()
    policy_object = GlobalSecurityPolicy.model_validate(config_data)
    policy_engine = PolicyEngine(policy_object)
    return LogService(policy_engine)


log_service_dependency = Annotated[LogService, Depends(get_log_service)]
