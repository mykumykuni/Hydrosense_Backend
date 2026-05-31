import httpx
from ..config import DJANGO_API_URL, DJANGO_API_KEY


async def forward_sensor_data(data: dict) -> dict:
    """POST a sensor reading to the Django backend's ingestion endpoint."""
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': DJANGO_API_KEY,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{DJANGO_API_URL}/api/sensors/readings/',
            json=data,
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
