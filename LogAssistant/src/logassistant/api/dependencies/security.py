from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from logassistant.services import AuthService

bearer_scheme = HTTPBearer()


class ClientCredentialsRequestForm:
    def __init__(
        self,
        grant_type: str = Form(pattern="client_credentials"),
        client_secret: str = Form(json_schema_extra={"format": "password"}),
        scope: str = Form(default=""),
    ):
        self.grant_type = grant_type
        self.client_secret = client_secret
        self.scopes = scope.split() if scope else []


async def verify_jwt_protection(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    token = credentials.credentials
    payload = AuthService.verify_machine_token(token)
    return payload


trusted_machine = Annotated[dict, Depends(verify_jwt_protection)]
