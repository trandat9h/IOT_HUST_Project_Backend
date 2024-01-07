from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from motor.core import AgnosticCollection
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from db import get_session
from models.gardens import GardenModel
from schemas.gardens import CreateGardenSchema, GardenSchema, UpdateGardenSchema

router = APIRouter(prefix="/gardens", tags=["gardens"])


@router.get(
    "/",
    response_model=list[GardenSchema],
    response_description="Get all gardens"
)
async def get_gardens(session: Annotated[AsyncSession, Depends(get_session)]):
    stmt = select(GardenModel)

    gardens = (await session.scalars(stmt)).all()
    return gardens


@router.post(
    "/",
    response_model=GardenSchema,
    response_description="Add new garden",
)
async def create_garden(
    data: CreateGardenSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    garden = GardenModel(**data.dict())
    session.add(garden)

    await session.commit()

    return garden


@router.get(
    "/{garden_id}",
    response_model=GardenSchema,
    response_description="Get garden by id",
)
async def get_garden_by_id(
    garden_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    stmt = select(GardenModel).where(GardenModel.id == garden_id).options()

    result = (await session.execute(stmt)).scalar_one_or_none()

    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Garden not found"}),
        )

    return result


@router.put(
    "/{garden_id}",
    response_model=GardenSchema,
    response_description="Update garden by id",
)
async def update_garden(
    garden_id: int,
    data: UpdateGardenSchema,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    stmt = select(GardenModel).where(GardenModel.id == garden_id).options()

    garden = (await session.execute(stmt)).scalar_one_or_none()

    if not garden:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"detail": "Garden not found"}),
        )

    if data.title:
        garden.title = data.title
    if data.description:
        garden.description = data.description
    if data.address:
        garden.address = data.address
    if data.status:
        garden.status = data.status

    await session.commit()

    return garden

