import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import MeasureDataModel, DeviceModel


async def get_device_latest_measure_data(
    session: AsyncSession,
    device: DeviceModel,
) -> str:
    stmt = (
        select(MeasureDataModel)
        .where(MeasureDataModel.device_id == device.id)
        .order_by(MeasureDataModel.timestamp.desc())
        .limit(1)
    )

    result = (await session.execute(stmt)).scalar_one_or_none()
    if not result:
        latest_measure_data = "No data"
    else:
        latest_measure_data = result.value
        latest_measure_data = f"{latest_measure_data}{device.device_type_model.unit}"

    return latest_measure_data


def get_device_id_by_access_token(access_token: str) -> int:
    # Decode the JWT token
    decoded_token = jwt.decode(access_token, "secret_key", algorithms=['HS256'], verify=False)

    # Retrieve device_id from the decoded token
    device_id = decoded_token.get('device_id')

    return int(device_id)
