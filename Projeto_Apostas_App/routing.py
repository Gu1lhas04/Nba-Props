"""
WebSocket URL Routing
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Jogos ao vivo
    re_path(r'ws/live-games/$', consumers.LiveGamesConsumer.as_asgi()),

    # Estatísticas de jogador específico
    re_path(r'ws/player-stats/(?P<player_id>\w+)/$', consumers.PlayerStatsConsumer.as_asgi()),

    # Atualizações de odds
    re_path(r'ws/odds/$', consumers.OddsConsumer.as_asgi()),

    # Notificações de apostas do usuário
    re_path(r'ws/bet-notifications/$', consumers.BetNotificationConsumer.as_asgi()),
]
