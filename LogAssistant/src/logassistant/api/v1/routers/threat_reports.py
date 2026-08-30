from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, Path, UploadFile, status
from logassistant.api.dependencies import (
    LogServiceDependency,
    ThreatServiceDependency,
    TrustedMachine,
)

router = APIRouter(prefix="/threat-raports")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_threat_raports(threat_service: ThreatServiceDependency):
    return await threat_service.get_threat_reports()


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_report(
    id: Annotated[int, Path(gt=0)], threat_service: ThreatServiceDependency
):
    return await threat_service.get_threat_report(id)


# DO AI: Analogicznie tutaj problemem jest depends i file jak w auth.py
@router.post("/process-batch", status_code=status.HTTP_202_ACCEPTED)
async def process_batch_data(
    background_tasks: BackgroundTasks,
    _auth: TrustedMachine,
    log_analyzer_service: LogServiceDependency,
    file: UploadFile = File(...),
):
    background_tasks.add_task(log_analyzer_service.run_analysis, file)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    id: Annotated[int, Path(gt=0)], threat_service: ThreatServiceDependency
):
    await threat_service.delete_threat_report(id)
