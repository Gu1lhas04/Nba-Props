"""
Sistema de atualização automática de dados em tempo real
Usa threading para atualizar jogos ao vivo e enviar via WebSocket
"""

import asyncio
import threading
import time
import logging
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from nba_api.live.nba.endpoints import scoreboard
from .mongodb_cache import nba_cache

logger = logging.getLogger(__name__)


class LiveGamesUpdater:
    """
    Atualiza jogos ao vivo automaticamente e transmite via WebSocket
    """

    def __init__(self, update_interval=10):
        """
        Args:
            update_interval: Intervalo de atualização em segundos (default: 10s)
        """
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.channel_layer = get_channel_layer()

    def start(self):
        """Inicia o sistema de atualização em background"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
            logger.info("🚀 LiveGamesUpdater iniciado")

    def stop(self):
        """Para o sistema de atualização"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("⏹️ LiveGamesUpdater parado")

    def _update_loop(self):
        """Loop principal de atualização"""
        while self.running:
            try:
                self._fetch_and_broadcast_live_games()
            except Exception as e:
                logger.error(f"❌ Erro no update loop: {e}")

            # Aguarda antes da próxima atualização
            time.sleep(self.update_interval)

    def _fetch_and_broadcast_live_games(self):
        """Busca jogos ao vivo da NBA API e transmite via WebSocket"""
        try:
            # Conecta ao MongoDB
            nba_cache.connect()

            # Busca jogos ao vivo
            board = scoreboard.ScoreBoard()
            games_data = board.get_dict()

            if not games_data or 'scoreboard' not in games_data:
                logger.warning("⚠️ Nenhum dado de scoreboard disponível")
                return

            games = games_data['scoreboard'].get('games', [])

            if not games:
                logger.info("ℹ️ Nenhum jogo ao vivo no momento")
                return

            live_games_list = []

            for game in games:
                try:
                    game_id = game.get('gameId', '')
                    home_team = game.get('homeTeam', {})
                    away_team = game.get('awayTeam', {})

                    game_info = {
                        'game_id': game_id,
                        'home_team': home_team.get('teamName', ''),
                        'away_team': away_team.get('teamName', ''),
                        'home_score': home_team.get('score', 0),
                        'away_score': away_team.get('score', 0),
                        'quarter': game.get('period', 0),
                        'time_remaining': game.get('gameClock', ''),
                        'status': self._get_game_status(game),
                        'game_status_text': game.get('gameStatusText', ''),
                    }

                    # Salva no cache MongoDB
                    nba_cache.set_live_game(game_id, game_info)
                    live_games_list.append(game_info)

                except Exception as e:
                    logger.error(f"❌ Erro ao processar jogo: {e}")
                    continue

            # Transmite para todos os clientes conectados via WebSocket
            if live_games_list:
                self._broadcast_to_websocket(live_games_list)
                logger.info(f"📡 Transmitidos {len(live_games_list)} jogos ao vivo")

        except Exception as e:
            logger.error(f"❌ Erro ao buscar jogos ao vivo: {e}")

    def _get_game_status(self, game):
        """Determina o status do jogo"""
        game_status = game.get('gameStatus', 0)

        # 1 = Not Started, 2 = Live, 3 = Finished
        if game_status == 1:
            return 'scheduled'
        elif game_status == 2:
            return 'live'
        elif game_status == 3:
            return 'final'
        else:
            return 'unknown'

    def _broadcast_to_websocket(self, games_data):
        """Transmite dados para clientes WebSocket"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'live_games',
                {
                    'type': 'game_update',
                    'data': {
                        'games': games_data,
                        'timestamp': datetime.now().isoformat(),
                        'count': len(games_data)
                    }
                }
            )
        except Exception as e:
            logger.error(f"❌ Erro ao transmitir via WebSocket: {e}")


class PlayerStatsUpdater:
    """
    Atualiza estatísticas de jogadores em jogos ao vivo
    """

    def __init__(self, update_interval=30):
        """
        Args:
            update_interval: Intervalo de atualização em segundos (default: 30s)
        """
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.channel_layer = get_channel_layer()
        self.tracked_players = set()  # Jogadores sendo rastreados

    def track_player(self, player_id):
        """Adiciona um jogador para rastreamento"""
        self.tracked_players.add(player_id)
        logger.info(f"👀 Rastreando jogador: {player_id}")

    def untrack_player(self, player_id):
        """Remove um jogador do rastreamento"""
        self.tracked_players.discard(player_id)
        logger.info(f"👋 Parou de rastrear jogador: {player_id}")

    def start(self):
        """Inicia o sistema de atualização"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
            logger.info("🚀 PlayerStatsUpdater iniciado")

    def stop(self):
        """Para o sistema de atualização"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("⏹️ PlayerStatsUpdater parado")

    def _update_loop(self):
        """Loop principal de atualização"""
        while self.running:
            try:
                if self.tracked_players:
                    self._update_tracked_players()
            except Exception as e:
                logger.error(f"❌ Erro no player stats update loop: {e}")

            time.sleep(self.update_interval)

    def _update_tracked_players(self):
        """Atualiza estatísticas dos jogadores rastreados"""
        # Esta função seria implementada para buscar stats atualizadas
        # e transmitir via WebSocket
        # Por enquanto é um placeholder
        pass


# Instâncias globais dos updaters
live_games_updater = LiveGamesUpdater(update_interval=10)
player_stats_updater = PlayerStatsUpdater(update_interval=30)
