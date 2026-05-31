from decouple import config

DJANGO_API_URL: str = config('DJANGO_API_URL', default='http://localhost:8000')
DJANGO_API_KEY: str = config('DJANGO_API_KEY', default='')
FASTAPI_PORT: int = config('FASTAPI_PORT', default=8001, cast=int)
CORS_ALLOWED_ORIGINS: list[str] = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:3001'
).split(',')
