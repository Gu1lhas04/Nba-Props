"""
Integração do sistema de odds com as views existentes
"""

import logging
from .odds_scrapers import odds_aggregator
from .mongodb_cache import nba_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OddsCache:
    """Cache de odds com MongoDB"""

    @staticmethod
    def get_cached_odds(player_name, stat_type):
        """
        Obtém odds do cache

        Returns:
            dict ou None
        """
        try:
            from .mongodb_models import PlayerOddsCache

            # Busca no cache
            cache = PlayerOddsCache.objects(
                player_name__iexact=player_name,
                stat_type=stat_type
            ).first()

            if cache and not cache.is_expired(ttl_seconds=300):  # 5 minutos
                logger.info(f"📊 Cache HIT - Odds: {player_name} {stat_type}")
                return {
                    'line': cache.line,
                    'over_odds': cache.over_odds,
                    'under_odds': cache.under_odds,
                    'source': cache.source
                }

            logger.info(f"💾 Cache MISS - Odds: {player_name} {stat_type}")
            return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar odds do cache: {e}")
            return None

    @staticmethod
    def set_cached_odds(player_name, stat_type, odds_data):
        """Salva odds no cache"""
        try:
            from .mongodb_models import PlayerOddsCache

            cache = PlayerOddsCache.objects(
                player_name__iexact=player_name,
                stat_type=stat_type
            ).first()

            if cache:
                cache.line = odds_data['line']
                cache.over_odds = odds_data['over_odds']
                cache.under_odds = odds_data['under_odds']
                cache.source = odds_data.get('source', 'Unknown')
                cache.updated_at = datetime.utcnow()
                cache.save()
            else:
                PlayerOddsCache(
                    player_name=player_name,
                    stat_type=stat_type,
                    line=odds_data['line'],
                    over_odds=odds_data['over_odds'],
                    under_odds=odds_data['under_odds'],
                    source=odds_data.get('source', 'Unknown')
                ).save()

            logger.info(f"✅ Odds cached: {player_name} {stat_type}")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar odds no cache: {e}")
            return False


def get_player_odds(player_name, stat_type='PTS'):
    """
    Função principal para obter odds de um jogador

    Args:
        player_name: Nome do jogador
        stat_type: Tipo de estatística (PTS, AST, REB, etc.)

    Returns:
        dict: {
            'line': float,
            'over_odds': float,
            'under_odds': float,
            'source': str,
            'cached': bool
        }
    """
    try:
        # Tenta buscar do cache primeiro
        cached_odds = OddsCache.get_cached_odds(player_name, stat_type)

        if cached_odds:
            cached_odds['cached'] = True
            return cached_odds

        # Se não estiver no cache, busca das APIs/scrapers
        logger.info(f"🔍 Buscando odds de fontes externas para {player_name} - {stat_type}")
        odds_data = odds_aggregator.get_best_odds(player_name, stat_type)

        if odds_data:
            # Salva no cache
            OddsCache.set_cached_odds(player_name, stat_type, odds_data)
            odds_data['cached'] = False
            return odds_data

        # Se não encontrou, retorna odds padrão baseadas em média
        logger.warning(f"⚠️ Usando odds padrão para {player_name} - {stat_type}")
        return {
            'line': 0,  # Será calculado pela média do jogador
            'over_odds': 1.90,
            'under_odds': 1.90,
            'source': 'Default',
            'cached': False
        }

    except Exception as e:
        logger.error(f"❌ Erro ao obter odds: {e}")
        return {
            'line': 0,
            'over_odds': 1.90,
            'under_odds': 1.90,
            'source': 'Error',
            'cached': False
        }


def get_multiple_players_odds(players_stats):
    """
    Obtém odds para múltiplos jogadores de uma vez

    Args:
        players_stats: List de dicts com 'player_name' e 'stat_type'

    Returns:
        dict: {player_name: {stat_type: odds_data}}
    """
    results = {}

    for player_stat in players_stats:
        player_name = player_stat['player_name']
        stat_type = player_stat.get('stat_type', 'PTS')

        if player_name not in results:
            results[player_name] = {}

        odds = get_player_odds(player_name, stat_type)
        results[player_name][stat_type] = odds

    return results


def refresh_popular_odds():
    """
    Atualiza odds dos jogadores mais populares em background
    Útil para pré-carregar o cache
    """
    popular_players = [
        'LeBron James',
        'Stephen Curry',
        'Kevin Durant',
        'Giannis Antetokounmpo',
        'Luka Doncic',
        'Nikola Jokic',
        'Joel Embiid',
        'Jayson Tatum',
        'Damian Lillard',
        'Anthony Davis'
    ]

    stat_types = ['PTS', 'AST', 'REB']

    logger.info(f"🔄 Atualizando odds de {len(popular_players)} jogadores populares...")

    updated_count = 0
    for player_name in popular_players:
        for stat_type in stat_types:
            try:
                odds = get_player_odds(player_name, stat_type)
                if odds and odds.get('line', 0) > 0:
                    updated_count += 1
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar {player_name}: {e}")
                continue

    logger.info(f"✅ {updated_count} odds atualizadas no cache")
    return updated_count
