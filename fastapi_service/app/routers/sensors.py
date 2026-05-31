from fastapi import APIRouter, HTTPException, status
import httpx
from ..schemas.sensor import SensorReadingSchema, SensorReadingResponse
from ..services.django_client import forward_sensor_data

router = APIRouter(prefix='/sensors', tags=['Sensor Ingestion'])


@router.post(
    '/ingest',
    response_model=SensorReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Ingest a multi-parameter sensor reading from an IoT device',
)
async def ingest_sensor_data(reading: SensorReadingSchema):
    payload = reading.model_dump(exclude_none=True)
    payload['timestamp'] = payload['timestamp'].isoformat()

    try:
        await forward_sensor_data(payload)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f'Django backend rejected the data: {exc.response.text}',
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f'Could not reach Django backend: {str(exc)}',
        )

    return SensorReadingResponse(
        success=True,
        message='Sensor reading received and forwarded to backend.',
        device_id=reading.device_id,
    )


@router.get('/health', summary='Health check for the ingestion service')
async def health_check():
    return {'status': 'ok', 'service': 'hydrosense-fastapi'}
