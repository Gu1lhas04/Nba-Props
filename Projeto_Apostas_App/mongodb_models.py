"""
MongoDB Models para cache de dados da NBA API
Usando MongoEngine para definir schemas de documentos
"""

from mongoengine import Document, StringField, IntField, FloatField, DictField, ListField, DateTimeField
from datetime import datetime


class PlayerStatsCache(Document):
    """Cache de estatísticas de jogadores"""
    player_id = IntField(required=True)
    player_name = StringField(required=True)
    season = StringField(required=True)  # Formato: "2024-25"
    stats_data = DictField()  # Armazena as estatísticas completas
    last_10_games = ListField(DictField())  # Últimos 10 jogos
    averages = DictField()  # Médias calculadas
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'player_stats',
        'indexes': [
            ('player_id', 'season'),  # Index composto
            'updated_at'
        ]
    }

    def is_expired(self, ttl_seconds=300):
        """Verifica se o cache expirou (default: 5 minutos)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds


class PlayerInfoCache(Document):
    """Cache de informações básicas de jogadores"""
    player_id = IntField(required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    team_name = StringField()
    team_id = IntField()
    height = StringField()
    weight = StringField()
    position = StringField()
    jersey = StringField()
    age = IntField()
    player_data = DictField()  # Dados completos do jogador
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'player_info',
        'indexes': ['player_id', 'updated_at']
    }

    def is_expired(self, ttl_seconds=3600):
        """Verifica se o cache expirou (default: 1 hora)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds


class LiveGameCache(Document):
    """Cache de jogos ao vivo"""
    game_id = StringField(required=True, unique=True)
    home_team = StringField()
    away_team = StringField()
    home_score = IntField()
    away_score = IntField()
    quarter = IntField()  # Mudado para IntField
    time_remaining = StringField()
    status = StringField()  # 'live', 'final', 'scheduled'
    game_data = DictField()  # Dados completos do jogo
    player_stats = ListField(DictField())  # Stats dos jogadores no jogo
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'live_games',
        'indexes': ['game_id', 'status', 'updated_at']
    }

    def is_expired(self, ttl_seconds=10):
        """Verifica se o cache expirou (default: 10 segundos para jogos ao vivo)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds


class GameScheduleCache(Document):
    """Cache de calendário de jogos"""
    date = StringField(required=True)  # Formato: YYYY-MM-DD
    games = ListField(DictField())  # Lista de jogos do dia
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'game_schedule',
        'indexes': ['date', 'updated_at']
    }

    def is_expired(self, ttl_seconds=600):
        """Verifica se o cache expirou (default: 10 minutos)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds


class TeamStatsCache(Document):
    """Cache de estatísticas de times"""
    team_id = IntField(required=True, unique=True)
    team_name = StringField()
    team_abbreviation = StringField()
    stats_data = DictField()  # Estatísticas completas
    roster = ListField(DictField())  # Elenco do time
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'team_stats',
        'indexes': ['team_id', 'updated_at']
    }

    def is_expired(self, ttl_seconds=3600):
        """Verifica se o cache expirou (default: 1 hora)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds


class PlayerOddsCache(Document):
    """Cache de odds e lines de jogadores"""
    player_name = StringField(required=True)
    stat_type = StringField(required=True)  # PTS, AST, REB, etc.
    line = FloatField(required=True)  # Linha/threshold
    over_odds = FloatField(default=1.90)  # Odds para over
    under_odds = FloatField(default=1.90)  # Odds para under
    source = StringField()  # Fonte dos dados (PrizePicks, etc.)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'player_odds',
        'indexes': [
            ('player_name', 'stat_type'),
            'updated_at'
        ]
    }

    def is_expired(self, ttl_seconds=300):
        """Verifica se o cache expirou (default: 5 minutos)"""
        if not self.updated_at:
            return True
        elapsed = (datetime.utcnow() - self.updated_at).total_seconds()
        return elapsed > ttl_seconds
