from fastapi import APIRouter, Depends
from logassistant.api.dependencies import ClientCredentialsRequestForm
from logassistant.services import AuthService

router = APIRouter(prefix="/auth", tags=["Auithentication"])


@router.post("/token")
# DO AI: Do not perform function call `Depends` in argument defaults; instead, perform the call within the function, or read the default from a module-level singleton variableRuffB008 - Co z tym zrobić?
async def get_access_token(form_data: ClientCredentialsRequestForm = Depends()):
    token = AuthService.authenticate_client(form_data.client_secret)
    return {"access_token": token, "token_type": "bearer"}
