from fastapi import Depends, Path
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from src.databases.payroll_db import get_sync_db as get_sync_pr_db
from sqlalchemy.orm import Session
from src.utils.positions import (
    read_positions,
    get_position_distribution,
    add_and_sync_position,
    update_and_sync_position,
    delete_and_sync_position,
)
from src.models.human import PositionUpdate, PositionCreate
from src.utils.auth import has_role
from src.models.user import Role
from src._utils import response

positions_router = APIRouter(prefix="", tags=["Positions"])


@positions_router.get("")
def get_positions(
    db: Session = Depends(get_sync_hm_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value, Role.PAYROLL_MANAGER.value])
    )
):
    return response(data=read_positions(session=db))


@positions_router.get("/distribution/{position_id}")
def get_numbers_of_position_by_department(
    position_id: int, 
    db: Session = Depends(get_sync_hm_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value, Role.PAYROLL_MANAGER.value])
    )
):
    return response(data=get_position_distribution(session=db, position_id=position_id))


@positions_router.post("/add")
def add_position(
    position: PositionCreate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=add_and_sync_position(
            session_human=hm_db, 
            session_payroll=pr_db, 
            position=position
        )
    )


@positions_router.put("/update/{position_id}")
def update_position(
    position_id: int,
    position: PositionUpdate,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=update_and_sync_position(
            session_human=hm_db,
            session_payroll=pr_db,
            position_id=position_id,
            position=position
        )
    )


@positions_router.delete("/delete/{position_id}")
def delete_position(
    position_id: int,
    hm_db: Session = Depends(get_sync_hm_db),
    pr_db: Session = Depends(get_sync_pr_db),
    has_role=Depends(
        has_role(required_roles=[Role.ADMIN.value, Role.HR_MANAGER.value])
    )
):
    return response(
        data=delete_and_sync_position(
            session_human=hm_db,
            session_payroll=pr_db,
            position_id=position_id
        )
    )
