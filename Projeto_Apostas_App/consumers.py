"""
WebSocket Consumers para atualizações em tempo real
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)


class LiveGamesConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações de jogos ao vivo em tempo real
    """

    async def connect(self):
        """Chamado quando o WebSocket é conectado"""
        self.room_group_name = 'live_games'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"🔗 WebSocket conectado: Live Games - {self.channel_name}")

    async def disconnect(self, close_code):
        """Chamado quando o WebSocket é desconectado"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"🔌 WebSocket desconectado: Live Games - {self.channel_name}")

    async def receive(self, text_data):
        """Recebe mensagens do WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Responde ao ping para manter conexão ativa
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")

    async def game_update(self, event):
        """Envia atualizações de jogo para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': event['data']
        }))


class PlayerStatsConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações de estatísticas de jogadores em tempo real
    """

    async def connect(self):
        """Chamado quando o WebSocket é conectado"""
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.room_group_name = f'player_stats_{self.player_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"🔗 WebSocket conectado: Player Stats {self.player_id} - {self.channel_name}")

    async def disconnect(self, close_code):
        """Chamado quando o WebSocket é desconectado"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"🔌 WebSocket desconectado: Player Stats {self.player_id} - {self.channel_name}")

    async def receive(self, text_data):
        """Recebe mensagens do WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")

    async def stats_update(self, event):
        """Envia atualizações de estatísticas para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': event['data']
        }))


class OddsConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações de odds em tempo real
    """

    async def connect(self):
        """Chamado quando o WebSocket é conectado"""
        self.room_group_name = 'odds_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"🔗 WebSocket conectado: Odds - {self.channel_name}")

    async def disconnect(self, close_code):
        """Chamado quando o WebSocket é desconectado"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"🔌 WebSocket desconectado: Odds - {self.channel_name}")

    async def receive(self, text_data):
        """Recebe mensagens do WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            elif message_type == 'subscribe':
                # Cliente quer se inscrever em um jogador específico
                player_id = data.get('player_id')
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'player_id': player_id
                }))
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")

    async def odds_update(self, event):
        """Envia atualizações de odds para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'odds_update',
            'data': event['data']
        }))


class BetNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer para notificações de apostas (ganhas/perdidas) em tempo real
    """

    async def connect(self):
        """Chamado quando o WebSocket é conectado"""
        self.user = self.scope['user']

        if self.user.is_authenticated:
            self.room_group_name = f'user_bets_{self.user.id}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"🔗 WebSocket conectado: Bet Notifications - User {self.user.id}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Chamado quando o WebSocket é desconectado"""
        if self.user.is_authenticated:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"🔌 WebSocket desconectado: Bet Notifications - User {self.user.id}")

    async def receive(self, text_data):
        """Recebe mensagens do WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")

    async def bet_notification(self, event):
        """Envia notificações de apostas para o WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'bet_notification',
            'data': event['data']
        }))
