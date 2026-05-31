from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import sensors
from .config import CORS_ALLOWED_ORIGINS

app = FastAPI(
    title='HydroSense Sensor Ingestion API',
    description='Receives IoT sensor readings and forwards them to the Django backend.',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(sensors.router, prefix='/api')


@app.get('/', tags=['Root'])
async def root():
    return {
        'service': 'HydroSense Sensor Ingestion',
        'docs': '/docs',
        'health': '/api/sensors/health',
    }
