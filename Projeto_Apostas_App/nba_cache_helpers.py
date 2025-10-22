"""
Helpers para integração entre views Django e MongoDB cache
"""

import logging
from .mongodb_cache import nba_cache
from nba_api.stats.endpoints import playergamelog, commonplayerinfo

logger = logging.getLogger(__name__)


def get_cached_player_info(player_id):
    """
    Obtém informações do jogador do cache ou busca da API

    Args:
        player_id: ID do jogador na NBA

    Returns:
        dict: Informações do jogador
    """
    try:
        # Conecta ao MongoDB
        nba_cache.connect()

        # Tenta buscar do cache
        cached_data = nba_cache.get_player_info(player_id)

        if cached_data:
            logger.info(f"✅ Player info obtida do cache: {player_id}")
            return cached_data

        # Se não estiver no cache, busca da API
        logger.info(f"🔍 Buscando player info da API: {player_id}")
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        player_data = player_info.get_normalized_dict()

        if player_data and 'CommonPlayerInfo' in player_data:
            info = player_data['CommonPlayerInfo'][0]

            # Salva no cache
            nba_cache.set_player_info(player_id, info)
            logger.info(f"💾 Player info salva no cache: {player_id}")

            return info

        return None

    except Exception as e:
        logger.error(f"❌ Erro ao obter player info: {e}")
        return None


def get_cached_player_stats(player_id, player_name, season=None):
    """
    Obtém estatísticas do jogador do cache ou busca da API

    Args:
        player_id: ID do jogador
        player_name: Nome do jogador
        season: Temporada (formato: 2024-25). Se None, usa temporada atual

    Returns:
        dict: Estatísticas do jogador com last_10_games e averages
    """
    try:
        # Conecta ao MongoDB
        nba_cache.connect()

        # Se season não foi especificada, usa a temporada atual
        if not season:
            from .season_helpers import get_current_season
            season = get_current_season()

        # Tenta buscar do cache
        cached_data = nba_cache.get_player_stats(player_id, season)

        if cached_data:
            logger.info(f"✅ Player stats obtida do cache: {player_id} (Season: {season})")
            return cached_data

        # Se não estiver no cache, busca da API
        logger.info(f"🔍 Buscando player stats da API: {player_id} (Season: {season})")

        # Busca logs de jogos
        import pandas as pd

        season_types = ["Regular Season", "Playoffs", "PlayIn"]
        all_logs = []

        for season_type in season_types:
            try:
                log = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season,
                    season_type_all_star=season_type
                ).get_data_frames()[0]

                if not log.empty:
                    log["SEASON_TYPE"] = season_type
                    all_logs.append(log)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar {season_type}: {e}")

        if not all_logs:
            return None

        # Junta todos os logs
        player_log = pd.concat(all_logs, ignore_index=True)

        # Processa estatísticas
        columns = ['GAME_DATE', 'MATCHUP', 'MIN', 'PTS', 'AST', 'REB', 'FG3M', 'BLK', 'STL', 'SEASON_TYPE']
        player_filtered = player_log[columns].copy()
        player_filtered['GAME_DATE'] = pd.to_datetime(player_filtered['GAME_DATE'])
        player_filtered = player_filtered.sort_values(by='GAME_DATE', ascending=False)

        # Últimos 10 jogos
        last_10_games = player_filtered.head(10).to_dict(orient='records')

        # Calcula médias
        averages = {
            'points': round(player_filtered['PTS'].mean(), 2),
            'assists': round(player_filtered['AST'].mean(), 2),
            'rebounds': round(player_filtered['REB'].mean(), 2),
            'three_point': round(player_filtered['FG3M'].mean(), 2),
            'blocks': round(player_filtered['BLK'].mean(), 2),
            'steals': round(player_filtered['STL'].mean(), 2),
        }

        stats_data = {
            'last_10_games': last_10_games,
            'averages': averages,
            'total_games': len(player_filtered),
            'season': season
        }

        # Salva no cache
        nba_cache.set_player_stats(
            player_id=player_id,
            player_name=player_name,
            season=season,
            stats_data=stats_data,
            last_10_games=last_10_games,
            averages=averages
        )
        logger.info(f"💾 Player stats salva no cache: {player_id} (Season: {season})")

        return stats_data

    except Exception as e:
        logger.error(f"❌ Erro ao obter player stats: {e}")
        return None


def get_cached_live_games():
    """
    Obtém jogos ao vivo do cache

    Returns:
        list: Lista de jogos ao vivo
    """
    try:
        # Conecta ao MongoDB
        nba_cache.connect()

        # Busca do cache
        games = nba_cache.get_live_games()

        if games:
            logger.info(f"✅ {len(games)} jogos ao vivo obtidos do cache")
            return games

        logger.info("ℹ️ Nenhum jogo ao vivo no cache")
        return []

    except Exception as e:
        logger.error(f"❌ Erro ao obter live games: {e}")
        return []


def invalidate_player_cache(player_id):
    """
    Invalida cache de um jogador específico

    Args:
        player_id: ID do jogador
    """
    try:
        from .mongodb_models import PlayerStatsCache, PlayerInfoCache

        # Remove do cache
        PlayerStatsCache.objects(player_id=player_id).delete()
        PlayerInfoCache.objects(player_id=player_id).delete()

        logger.info(f"🗑️ Cache invalidado para jogador: {player_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao invalidar cache: {e}")
        return False
