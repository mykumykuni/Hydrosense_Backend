from django.urls import re_path
from .consumers import HydroSenseConsumer

websocket_urlpatterns = [
    re_path(r'^ws/$', HydroSenseConsumer.as_asgi()),
]
