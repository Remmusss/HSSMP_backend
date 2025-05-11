from fastapi import Depends, Path
from fastapi.routing import APIRouter
from src.databases.human_db import get_sync_db as get_sync_hm_db
from sqlalchemy.orm import Session
from src.utils.positions import read_positions, get_position_distribution
from src._utils import response

positions_router = APIRouter(prefix="", tags=["Positions"])

@positions_router.get("")
def get_positions(
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=read_positions(
            session=db
        )
    )

@positions_router.get("/distribution/{position_id}")
def get_numbers_of_position_by_department(
    position_id: int,
    db: Session = Depends(get_sync_hm_db)
):
    return response(
        data=get_position_distribution(
            session=db,
            position_id=position_id
        )
    ) 