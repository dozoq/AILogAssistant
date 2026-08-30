from fastapi import APIRouter

from .routers.auth import router as AuthRouter
from .routers.root import router as RootRouter
from .routers.threat_reports import router as ThreatRaportRouter

main_router = APIRouter()
main_router.include_router(ThreatRaportRouter)
main_router.include_router(RootRouter)
main_router.include_router(AuthRouter)
