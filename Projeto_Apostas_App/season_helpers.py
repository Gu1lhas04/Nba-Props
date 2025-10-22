"""
Helpers para gerenciar múltiplas temporadas de jogadores
"""

import logging
from datetime import datetime
from nba_api.stats.endpoints import playercareerstats
from .mongodb_cache import nba_cache

logger = logging.getLogger(__name__)


def get_current_season():
    """
    Retorna a temporada atual no formato NBA (ex: "2024-25")

    A temporada NBA vai de Outubro a Junho do ano seguinte.
    Por exemplo, a temporada 2024-25 vai de Out/2024 a Jun/2025.
    """
    now = datetime.now()
    year = now.year
    month = now.month

    # A temporada NBA começa em outubro
    # Se estamos entre Outubro-Dezembro, a temporada é ano_atual até ano_seguinte
    # Se estamos entre Janeiro-Setembro, a temporada começou no ano anterior
    if month >= 10:  # Outubro, Novembro, Dezembro
        start_year = year - 1  # Corrigido: se estamos em Out/2025, a temporada é 2024-25
        end_year = year
    else:  # Janeiro a Setembro
        start_year = year - 1
        end_year = year

    return f"{start_year}-{str(end_year)[-2:]}"


def get_available_seasons(player_id):
    """
    Obtém todas as temporadas disponíveis para um jogador

    Args:
        player_id: ID do jogador

    Returns:
        list: Lista de temporadas no formato ["2024-25", "2023-24", ...]
    """
    try:
        # Primeiro tenta buscar do cache MongoDB
        cached_seasons = nba_cache.get_player_seasons(player_id)

        if cached_seasons:
            logger.info(f"📅 Temporadas obtidas do cache para {player_id}: {cached_seasons}")
            return cached_seasons

        # Se não estiver no cache, busca da API
        logger.info(f"🔍 Buscando temporadas da API para jogador {player_id}")

        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        career_data = career_stats.get_normalized_dict()

        if not career_data or 'SeasonTotalsRegularSeason' not in career_data:
            return [get_current_season()]

        seasons = []
        for season_data in career_data['SeasonTotalsRegularSeason']:
            season = season_data.get('SEASON_ID')
            if season:
                seasons.append(season)

        # Remove duplicatas e ordena (mais recente primeiro)
        seasons = sorted(list(set(seasons)), reverse=True)

        logger.info(f"✅ Encontradas {len(seasons)} temporadas para jogador {player_id}")
        return seasons

    except Exception as e:
        logger.error(f"❌ Erro ao buscar temporadas do jogador {player_id}: {e}")
        # Retorna pelo menos a temporada atual
        return [get_current_season()]


def parse_season_years(season_string):
    """
    Converte string de temporada em anos

    Args:
        season_string: String no formato "2024-25"

    Returns:
        tuple: (ano_inicio, ano_fim) ex: (2024, 2025)
    """
    try:
        parts = season_string.split('-')
        start_year = int(parts[0])

        if len(parts[1]) == 2:
            end_year = int(f"{parts[0][:2]}{parts[1]}")
        else:
            end_year = int(parts[1])

        return start_year, end_year
    except Exception as e:
        logger.error(f"❌ Erro ao parsear temporada '{season_string}': {e}")
        return None, None


def format_season_display(season_string):
    """
    Formata temporada para exibição amigável

    Args:
        season_string: String no formato "2024-25"

    Returns:
        str: String formatada "2024-2025"
    """
    start_year, end_year = parse_season_years(season_string)

    if start_year and end_year:
        return f"{start_year}-{end_year}"

    return season_string


def get_season_range():
    """
    Retorna lista de temporadas dos últimos 10 anos

    Returns:
        list: Lista de temporadas ["2024-25", "2023-24", ...]
    """
    current_season = get_current_season()
    start_year = int(current_season.split('-')[0])

    seasons = []
    for i in range(10):  # Últimas 10 temporadas
        year = start_year - i
        next_year = year + 1
        season = f"{year}-{str(next_year)[-2:]}"
        seasons.append(season)

    return seasons
