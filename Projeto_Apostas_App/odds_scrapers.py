"""
Sistema de obtenção de odds e lines de múltiplas fontes gratuitas

FONTES IMPLEMENTADAS:
1. Odds API (api-sports.io) - 100 requests/dia grátis
2. The Rundown API - Gratuito
3. Scraping de sites públicos (backup)
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class OddsProvider:
    """Classe base para provedores de odds"""

    def get_player_props(self, player_name, stat_type):
        """
        Obtém props de um jogador

        Args:
            player_name: Nome do jogador
            stat_type: Tipo de stat (PTS, AST, REB, etc.)

        Returns:
            dict: {'line': float, 'over_odds': float, 'under_odds': float}
        """
        raise NotImplementedError


class TheOddsAPIProvider(OddsProvider):
    """
    The Odds API - https://the-odds-api.com/
    Free tier: 500 requests/mês
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or "demo"  # Use 'demo' para testes limitados
        self.base_url = "https://api.the-odds-api.com/v4"

    def get_player_props(self, player_name, stat_type='points'):
        """Obtém props do The Odds API"""
        try:
            # Mapeia stat types
            stat_map = {
                'PTS': 'player_points',
                'AST': 'player_assists',
                'REB': 'player_rebounds',
                'BLK': 'player_blocks',
                'STL': 'player_steals',
                '3PT': 'player_threes',
            }

            market = stat_map.get(stat_type, 'player_points')

            # Endpoint para props de jogadores
            url = f"{self.base_url}/sports/basketball_nba/events"

            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': market,
                'oddsFormat': 'decimal'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ The Odds API: Dados obtidos com sucesso")
                return self._parse_odds_api_response(data, player_name, stat_type)
            else:
                logger.warning(f"⚠️ The Odds API retornou status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar do The Odds API: {e}")
            return None

    def _parse_odds_api_response(self, data, player_name, stat_type):
        """Parseia resposta do The Odds API"""
        # Esta função precisa ser customizada com base na resposta real da API
        # Por enquanto retorna None
        return None


class PropSwapScraper(OddsProvider):
    """
    Scraper para PropSwap (site público com odds)
    """

    def __init__(self):
        self.base_url = "https://propswap.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_player_props(self, player_name, stat_type='PTS'):
        """Scraping de PropSwap"""
        try:
            # Normaliza nome do jogador
            player_slug = player_name.lower().replace(' ', '-')

            # URL de exemplo
            url = f"{self.base_url}/nba/players/{player_slug}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_propswap_html(soup, stat_type)
            else:
                logger.warning(f"⚠️ PropSwap retornou status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao fazer scraping de PropSwap: {e}")
            return None

    def _parse_propswap_html(self, soup, stat_type):
        """Parseia HTML do PropSwap"""
        # Implementação específica do site
        return None


class PrizePicksScraper(OddsProvider):
    """
    Scraper para PrizePicks - Popular para props
    """

    def __init__(self):
        self.base_url = "https://api.prizepicks.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://app.prizepicks.com/',
            'Origin': 'https://app.prizepicks.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    def get_player_props(self, player_name, stat_type='PTS'):
        """Obtém props do PrizePicks via API pública"""
        try:
            # PrizePicks tem uma API pública não documentada
            url = f"{self.base_url}/projections"

            params = {
                'league_id': '7',  # 7 = NBA
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ PrizePicks: {len(data.get('data', []))} projections obtidas")
                return self._parse_prizepicks_response(data, player_name, stat_type)
            else:
                logger.warning(f"⚠️ PrizePicks retornou status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar do PrizePicks: {e}")
            return None

    def _parse_prizepicks_response(self, data, player_name, stat_type):
        """Parseia resposta do PrizePicks"""
        try:
            # Mapeia tipos de stats
            stat_map = {
                'PTS': 'Points',
                'AST': 'Assists',
                'REB': 'Rebounds',
                'BLK': 'Blocks',
                'STL': 'Steals',
                '3PT': 'Threes',
                'PTS+AST': 'Pts+Asts',
                'PTS+REB': 'Pts+Rebs',
                'AST+REB': 'Asts+Rebs',
                'PTS+AST+REB': 'Pts+Asts+Rebs',
            }

            stat_name = stat_map.get(stat_type, 'Points')
            player_name_lower = player_name.lower()

            # Procura nas projections
            projections = data.get('data', [])
            included = data.get('included', [])

            # Cria mapa de jogadores
            players_map = {}
            for item in included:
                if item.get('type') == 'new_player':
                    players_map[item['id']] = item['attributes']

            # Procura projection do jogador
            for proj in projections:
                attrs = proj.get('attributes', {})
                relationships = proj.get('relationships', {})

                # Verifica se é o stat type correto
                if attrs.get('stat_type') != stat_name:
                    continue

                # Pega dados do jogador
                player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                if not player_id:
                    continue

                player_data = players_map.get(player_id, {})
                full_name = f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip().lower()

                if player_name_lower in full_name or full_name in player_name_lower:
                    line = float(attrs.get('line_score', 0))

                    # PrizePicks não fornece odds, usamos odds padrão
                    return {
                        'line': line,
                        'over_odds': 1.90,  # Odds aproximadas
                        'under_odds': 1.90,
                        'source': 'PrizePicks'
                    }

            logger.info(f"⚠️ Jogador '{player_name}' não encontrado no PrizePicks para {stat_type}")
            return None

        except Exception as e:
            logger.error(f"❌ Erro ao parsear resposta do PrizePicks: {e}")
            return None


class UnderdogFantasyScraper(OddsProvider):
    """
    Scraper para Underdog Fantasy - Outra fonte popular
    """

    def __init__(self):
        self.base_url = "https://api.underdogfantasy.com/beta/v5"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_player_props(self, player_name, stat_type='PTS'):
        """Obtém props do Underdog Fantasy"""
        try:
            url = f"{self.base_url}/over-under-lines"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Underdog Fantasy: Dados obtidos")
                return self._parse_underdog_response(data, player_name, stat_type)
            else:
                logger.warning(f"⚠️ Underdog Fantasy retornou status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar do Underdog Fantasy: {e}")
            return None

    def _parse_underdog_response(self, data, player_name, stat_type):
        """Parseia resposta do Underdog Fantasy"""
        # Implementação específica
        return None


class OddsAggregator:
    """
    Agrega odds de múltiplas fontes com sistema de fallback
    """

    def __init__(self):
        # Import fallback providers
        try:
            from .odds_fallback import StatisticalOddsProvider
            statistical_provider = StatisticalOddsProvider()
        except:
            statistical_provider = None

        self.providers = [
            PrizePicksScraper(),
            # TheOddsAPIProvider(),  # Requer API key
            # UnderdogFantasyScraper(),
            # PropSwapScraper(),
        ]

        # Adiciona fallback estatístico se disponível
        if statistical_provider:
            self.providers.append(statistical_provider)

    def get_best_odds(self, player_name, stat_type='PTS'):
        """
        Tenta obter odds de múltiplas fontes e retorna a melhor

        Returns:
            dict: {
                'line': float,
                'over_odds': float,
                'under_odds': float,
                'source': str,
                'timestamp': datetime
            }
        """
        logger.info(f"🔍 Buscando odds para {player_name} - {stat_type}")

        for provider in self.providers:
            try:
                provider_name = provider.__class__.__name__
                logger.info(f"📡 Tentando {provider_name}...")

                result = provider.get_player_props(player_name, stat_type)

                if result and result.get('line', 0) > 0:
                    result['timestamp'] = datetime.now()
                    result['source'] = provider_name
                    logger.info(f"✅ Odds obtidas de {provider_name}: Line={result['line']}")
                    return result

                # Delay entre tentativas
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Erro com {provider_name}: {e}")
                continue

        logger.warning(f"⚠️ Nenhuma fonte retornou odds para {player_name} - {stat_type}")
        return None

    def get_all_sources(self, player_name, stat_type='PTS'):
        """
        Obtém odds de todas as fontes disponíveis para comparação

        Returns:
            list: Lista de dicts com odds de cada fonte
        """
        results = []

        for provider in self.providers:
            try:
                result = provider.get_player_props(player_name, stat_type)

                if result:
                    result['timestamp'] = datetime.now()
                    result['source'] = provider.__class__.__name__
                    results.append(result)

                time.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Erro: {e}")
                continue

        return results


# Instância global do agregador
odds_aggregator = OddsAggregator()
