"""
Gerenciador de Cache MongoDB para dados da NBA API
"""

from mongoengine import connect, disconnect
from django.conf import settings
from datetime import datetime
import logging
from .mongodb_models import (
    PlayerStatsCache,
    PlayerInfoCache,
    LiveGameCache,
    GameScheduleCache,
    TeamStatsCache
)

logger = logging.getLogger(__name__)


class NBAMongoCache:
    """Singleton para gerenciar conexão e operações com MongoDB"""

    _instance = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NBAMongoCache, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Conecta ao MongoDB"""
        if not self._connected:
            try:
                connect(
                    db=settings.MONGODB_SETTINGS['db'],
                    host=settings.MONGODB_SETTINGS['host'],
                    port=settings.MONGODB_SETTINGS['port'],
                    username=settings.MONGODB_SETTINGS.get('username'),
                    password=settings.MONGODB_SETTINGS.get('password'),
                    authentication_source='admin',
                    alias='default'
                )
                self._connected = True
                logger.info("✅ Conectado ao MongoDB com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao conectar ao MongoDB: {e}")
                raise

    def disconnect(self):
        """Desconecta do MongoDB"""
        if self._connected:
            disconnect()
            self._connected = False
            logger.info("🔌 Desconectado do MongoDB")

    # ==========================================
    # PLAYER STATS CACHE
    # ==========================================

    def get_player_stats(self, player_id, season=None):
        """Obtém estatísticas de um jogador do cache para uma temporada específica"""
        try:
            if season:
                cache = PlayerStatsCache.objects(player_id=player_id, season=season).first()
            else:
                # Busca a temporada mais recente se não especificada
                cache = PlayerStatsCache.objects(player_id=player_id).order_by('-season').first()

            if cache and not cache.is_expired(settings.NBA_CACHE_SETTINGS['PLAYER_STATS_TTL']):
                logger.info(f"📊 Cache HIT - Player Stats: {player_id} (Season: {cache.season})")
                return cache.stats_data

            logger.info(f"💾 Cache MISS - Player Stats: {player_id} (Season: {season})")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar player stats cache: {e}")
            return None

    def set_player_stats(self, player_id, player_name, season, stats_data, last_10_games=None, averages=None):
        """Armazena estatísticas de um jogador no cache para uma temporada específica"""
        try:
            cache = PlayerStatsCache.objects(player_id=player_id, season=season).first()

            if cache:
                cache.player_name = player_name
                cache.stats_data = stats_data
                cache.last_10_games = last_10_games or []
                cache.averages = averages or {}
                cache.updated_at = datetime.utcnow()
                cache.save()
            else:
                PlayerStatsCache(
                    player_id=player_id,
                    player_name=player_name,
                    season=season,
                    stats_data=stats_data,
                    last_10_games=last_10_games or [],
                    averages=averages or {}
                ).save()

            logger.info(f"✅ Player stats cached: {player_id} (Season: {season})")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar player stats cache: {e}")
            return False

    def get_player_seasons(self, player_id):
        """Obtém lista de temporadas disponíveis para um jogador"""
        try:
            seasons = PlayerStatsCache.objects(player_id=player_id).distinct('season')
            seasons_sorted = sorted(seasons, reverse=True)  # Mais recentes primeiro

            if seasons_sorted:
                logger.info(f"📅 Temporadas encontradas no cache para {player_id}: {seasons_sorted}")
                return seasons_sorted

            return []
        except Exception as e:
            logger.error(f"❌ Erro ao buscar temporadas do jogador: {e}")
            return []

    # ==========================================
    # PLAYER INFO CACHE
    # ==========================================

    def get_player_info(self, player_id):
        """Obtém informações básicas de um jogador do cache"""
        try:
            cache = PlayerInfoCache.objects(player_id=player_id).first()

            if cache and not cache.is_expired(settings.NBA_CACHE_SETTINGS['PLAYER_INFO_TTL']):
                logger.info(f"👤 Cache HIT - Player Info: {player_id}")
                return cache.player_data

            logger.info(f"💾 Cache MISS - Player Info: {player_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar player info cache: {e}")
            return None

    def set_player_info(self, player_id, player_data):
        """Armazena informações básicas de um jogador no cache"""
        try:
            cache = PlayerInfoCache.objects(player_id=player_id).first()

            if cache:
                cache.first_name = player_data.get('FIRST_NAME')
                cache.last_name = player_data.get('LAST_NAME')
                cache.team_name = player_data.get('TEAM_NAME')
                cache.team_id = player_data.get('TEAM_ID')
                cache.height = player_data.get('HEIGHT')
                cache.weight = player_data.get('WEIGHT')
                cache.position = player_data.get('POSITION')
                cache.jersey = player_data.get('JERSEY')
                cache.age = player_data.get('AGE')
                cache.player_data = player_data
                cache.updated_at = datetime.utcnow()
                cache.save()
            else:
                PlayerInfoCache(
                    player_id=player_id,
                    first_name=player_data.get('FIRST_NAME'),
                    last_name=player_data.get('LAST_NAME'),
                    team_name=player_data.get('TEAM_NAME'),
                    team_id=player_data.get('TEAM_ID'),
                    height=player_data.get('HEIGHT'),
                    weight=player_data.get('WEIGHT'),
                    position=player_data.get('POSITION'),
                    jersey=player_data.get('JERSEY'),
                    age=player_data.get('AGE'),
                    player_data=player_data
                ).save()

            logger.info(f"✅ Player info cached: {player_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar player info cache: {e}")
            return False

    # ==========================================
    # LIVE GAMES CACHE
    # ==========================================

    def get_live_games(self):
        """Obtém todos os jogos ao vivo do cache"""
        try:
            games = LiveGameCache.objects(status='live')

            valid_games = []
            for game in games:
                if not game.is_expired(settings.NBA_CACHE_SETTINGS['LIVE_GAMES_TTL']):
                    valid_games.append(game.game_data)

            if valid_games:
                logger.info(f"🏀 Cache HIT - Live Games: {len(valid_games)} jogos")
                return valid_games

            logger.info("💾 Cache MISS - Live Games")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar live games cache: {e}")
            return None

    def set_live_game(self, game_id, game_data):
        """Armazena um jogo ao vivo no cache"""
        try:
            cache = LiveGameCache.objects(game_id=game_id).first()

            if cache:
                cache.home_team = game_data.get('home_team')
                cache.away_team = game_data.get('away_team')
                cache.home_score = game_data.get('home_score')
                cache.away_score = game_data.get('away_score')
                cache.quarter = game_data.get('quarter')
                cache.time_remaining = game_data.get('time_remaining')
                cache.status = game_data.get('status', 'live')
                cache.game_data = game_data
                cache.player_stats = game_data.get('player_stats', [])
                cache.updated_at = datetime.utcnow()
                cache.save()
            else:
                LiveGameCache(
                    game_id=game_id,
                    home_team=game_data.get('home_team'),
                    away_team=game_data.get('away_team'),
                    home_score=game_data.get('home_score'),
                    away_score=game_data.get('away_score'),
                    quarter=game_data.get('quarter'),
                    time_remaining=game_data.get('time_remaining'),
                    status=game_data.get('status', 'live'),
                    game_data=game_data,
                    player_stats=game_data.get('player_stats', [])
                ).save()

            logger.info(f"✅ Live game cached: {game_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar live game cache: {e}")
            return False

    # ==========================================
    # GAME SCHEDULE CACHE
    # ==========================================

    def get_game_schedule(self, date):
        """Obtém calendário de jogos de uma data específica"""
        try:
            cache = GameScheduleCache.objects(date=date).first()

            if cache and not cache.is_expired(settings.NBA_CACHE_SETTINGS['GAME_SCHEDULE_TTL']):
                logger.info(f"📅 Cache HIT - Schedule: {date}")
                return cache.games

            logger.info(f"💾 Cache MISS - Schedule: {date}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar schedule cache: {e}")
            return None

    def set_game_schedule(self, date, games):
        """Armazena calendário de jogos de uma data"""
        try:
            cache = GameScheduleCache.objects(date=date).first()

            if cache:
                cache.games = games
                cache.updated_at = datetime.utcnow()
                cache.save()
            else:
                GameScheduleCache(
                    date=date,
                    games=games
                ).save()

            logger.info(f"✅ Schedule cached: {date}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar schedule cache: {e}")
            return False


# Instância global do cache
nba_cache = NBAMongoCache()
