import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

GROUP_NAME = 'hydrosense'


class HydroSenseConsumer(AsyncWebsocketConsumer):
    """Single broadcast channel for all authenticated clients.

    Connect:  ws://localhost:8000/ws/?token=<access_jwt>

    Incoming client messages:
      { "type": "ping" }  →  { "type": "pong" }

    Server-pushed events:
      { "type": "sensor.reading", "data": { ... } }
      { "type": "alert.new",      "data": { ... } }
      { "type": "alert.resolved", "data": { ... } }
    """

    async def connect(self):
        token_str = self._get_token()
        self.user = await self._authenticate(token_str)

        if self.user is None:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        await self.accept()
        await self.send(json.dumps({
            'type': 'connection.established',
            'message': f'Connected as {self.user.email}',
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get('type') == 'ping':
            await self.send(json.dumps({'type': 'pong'}))

    # ── Group message handlers ──────────────────────────────────────────
    # Method name = event type with dots replaced by underscores

    async def sensor_reading(self, event):
        await self.send(json.dumps({'type': 'sensor.reading', 'data': event['data']}))

    async def alert_new(self, event):
        await self.send(json.dumps({'type': 'alert.new', 'data': event['data']}))

    async def alert_resolved(self, event):
        await self.send(json.dumps({'type': 'alert.resolved', 'data': event['data']}))

    # ── Helpers ─────────────────────────────────────────────────────────

    def _get_token(self):
        query_string = self.scope.get('query_string', b'').decode()
        params = {}
        for part in query_string.split('&'):
            if '=' in part:
                k, v = part.split('=', 1)
                params[k] = v
        return params.get('token', '')

    @database_sync_to_async
    def _authenticate(self, token_str):
        if not token_str:
            return None
        try:
            validated = AccessToken(token_str)
            user = User.objects.select_related('profile').get(pk=validated['user_id'])
            if user.status != 'active':
                return None
            if user.revoked_since and validated['iat'] < user.revoked_since.timestamp():
                return None
            return user
        except Exception:
            return None
