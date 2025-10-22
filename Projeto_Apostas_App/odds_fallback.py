"""
Sistema de fallback para odds quando APIs externas falham
Calcula lines baseadas nas médias dos jogadores
"""

import logging
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd

logger = logging.getLogger(__name__)


class StatisticalOddsProvider:
    """
    Provedor de odds baseado em estatísticas reais do jogador
    Usa NBA API para calcular médias e definir lines
    """

    def get_player_props(self, player_name, stat_type='PTS'):
        """
        Calcula line baseada na média do jogador

        Returns:
            dict: {'line': float, 'over_odds': 1.90, 'under_odds': 1.90}
        """
        try:
            logger.info(f"📊 Calculando odds estatísticas para {player_name} - {stat_type}")

            # Busca ID do jogador
            player_dict = players.find_players_by_full_name(player_name)

            if not player_dict:
                logger.warning(f"⚠️ Jogador '{player_name}' não encontrado")
                return None

            player_id = player_dict[0]['id']

            # Busca estatísticas da temporada atual
            from .season_helpers import get_current_season
            season = get_current_season()

            # Busca logs de jogos
            try:
                game_log = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season,
                    season_type_all_star='Regular Season'
                ).get_data_frames()[0]

                if game_log.empty:
                    logger.warning(f"⚠️ Sem jogos para {player_name} na temporada {season}")
                    return None

                # Calcula line e odds baseadas nas estatísticas
                line, over_odds, under_odds = self._calculate_line_and_odds(game_log, stat_type)

                if line and line > 0:
                    logger.info(f"✅ Line calculada: {line} para {stat_type} (Over: {over_odds}, Under: {under_odds})")
                    return {
                        'line': line,
                        'over_odds': over_odds,
                        'under_odds': under_odds,
                        'source': 'Statistical'
                    }

                return None

            except Exception as e:
                logger.error(f"❌ Erro ao buscar game log: {e}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro em StatisticalOddsProvider: {e}")
            return None

    def _calculate_line_and_odds(self, game_log, stat_type):
        """
        Calcula line (sempre terminando em .5) e odds baseadas na consistência

        Returns:
            tuple: (line, over_odds, under_odds)
        """
        try:
            import numpy as np

            # Calcula média e desvio padrão para o stat type
            if stat_type == 'PTS':
                values = game_log['PTS']
            elif stat_type == 'AST':
                values = game_log['AST']
            elif stat_type == 'REB':
                values = game_log['REB']
            elif stat_type == '3PT' or stat_type == 'FG3M':
                values = game_log['FG3M']
            elif stat_type == 'BLK':
                values = game_log['BLK']
            elif stat_type == 'STL':
                values = game_log['STL']
            elif stat_type == 'PTS+AST':
                values = game_log['PTS'] + game_log['AST']
            elif stat_type == 'PTS+REB':
                values = game_log['PTS'] + game_log['REB']
            elif stat_type == 'AST+REB':
                values = game_log['AST'] + game_log['REB']
            elif stat_type == 'PTS+AST+REB':
                values = game_log['PTS'] + game_log['AST'] + game_log['REB']
            else:
                logger.warning(f"⚠️ Stat type '{stat_type}' não reconhecido")
                return None, None, None

            mean_value = values.mean()
            std_dev = values.std()

            # Arredonda para sempre terminar em .5
            # Exemplos: 24.3 -> 24.5, 24.7 -> 24.5, 25.1 -> 25.5
            line = self._round_to_half(mean_value)

            # Calcula odds baseadas na consistência (desvio padrão)
            # Jogador mais consistente (baixo desvio) = odds mais próximas de 1.90
            # Jogador inconsistente (alto desvio) = odds variadas
            over_odds, under_odds = self._calculate_odds_from_consistency(
                mean_value, line, std_dev, values
            )

            return line, over_odds, under_odds

        except Exception as e:
            logger.error(f"❌ Erro ao calcular line e odds: {e}")
            return None, None, None

    def _round_to_half(self, value):
        """
        Arredonda valor para sempre terminar em .5

        Exemplos:
            24.3 -> 24.5
            24.7 -> 24.5
            25.1 -> 25.5
            25.8 -> 25.5
        """
        import math
        # Arredonda para o inteiro mais próximo, depois adiciona .5
        base = math.floor(value)
        return base + 0.5

    def _calculate_odds_from_consistency(self, mean, line, std_dev, values):
        """
        Calcula odds baseadas na probabilidade real de over/under

        Args:
            mean: Média do jogador
            line: Linha de aposta (sempre .5)
            std_dev: Desvio padrão
            values: Série de valores históricos

        Returns:
            tuple: (over_odds, under_odds)
        """
        try:
            # Calcula probabilidade empírica de OVER
            over_count = (values > line).sum()
            total_games = len(values)
            over_probability = over_count / total_games if total_games > 0 else 0.5

            # Ajusta para odds realistas (casas de apostas sempre tem margem)
            # Odds = 1 / probabilidade, mas com margem da casa (vig ~5%)
            margin = 0.05

            if over_probability > 0.05 and over_probability < 0.95:
                # Odds de Over
                over_odds = (1 / over_probability) * (1 - margin)
                # Odds de Under
                under_odds = (1 / (1 - over_probability)) * (1 - margin)
            else:
                # Valores extremos, usa odds padrão
                over_odds = 1.90
                under_odds = 1.90

            # Limita odds entre 1.50 e 2.50 (range realista de casas de apostas)
            over_odds = max(1.50, min(2.50, over_odds))
            under_odds = max(1.50, min(2.50, under_odds))

            # Arredonda para 2 casas decimais
            over_odds = round(over_odds, 2)
            under_odds = round(under_odds, 2)

            return over_odds, under_odds

        except Exception as e:
            logger.error(f"❌ Erro ao calcular odds: {e}")
            # Fallback para odds padrão
            return 1.90, 1.90


class SimplifiedOddsProvider:
    """
    Provedor simplificado que usa valores típicos por posição
    Usado como último recurso
    """

    # Médias típicas por posição
    POSITION_AVERAGES = {
        'Guard': {
            'PTS': 18.0,
            'AST': 5.0,
            'REB': 4.0,
            '3PT': 2.0,
            'STL': 1.0,
            'BLK': 0.3,
        },
        'Forward': {
            'PTS': 16.0,
            'AST': 3.0,
            'REB': 7.0,
            '3PT': 1.5,
            'STL': 0.8,
            'BLK': 0.8,
        },
        'Center': {
            'PTS': 14.0,
            'AST': 2.0,
            'REB': 10.0,
            '3PT': 0.5,
            'STL': 0.6,
            'BLK': 1.5,
        }
    }

    def get_player_props(self, player_name, stat_type='PTS'):
        """
        Retorna odds baseadas em médias de posição

        Returns:
            dict: {'line': float, 'over_odds': 1.90, 'under_odds': 1.90}
        """
        try:
            logger.info(f"📐 Usando médias de posição para {player_name} - {stat_type}")

            # Busca posição do jogador
            player_dict = players.find_players_by_full_name(player_name)

            if not player_dict:
                # Se não encontrar, usa médias de Guard (mais comum)
                position = 'Guard'
            else:
                # Determina posição baseada no nome/tipo
                # Simplificado - você pode melhorar isso consultando a API
                position = 'Guard'  # Default

            # Busca linha típica para a posição e stat
            line = self._get_position_average(position, stat_type)

            if line:
                logger.info(f"✅ Usando média de posição {position}: {line}")
                return {
                    'line': line,
                    'over_odds': 1.90,
                    'under_odds': 1.90,
                    'source': 'PositionAverage'
                }

            return None

        except Exception as e:
            logger.error(f"❌ Erro em SimplifiedOddsProvider: {e}")
            return None

    def _get_position_average(self, position, stat_type):
        """Retorna média típica para posição e stat"""
        try:
            base_stats = self.POSITION_AVERAGES.get(position, self.POSITION_AVERAGES['Guard'])

            if stat_type in base_stats:
                return base_stats[stat_type]

            # Stats combinadas
            if stat_type == 'PTS+AST':
                return base_stats['PTS'] + base_stats['AST']
            elif stat_type == 'PTS+REB':
                return base_stats['PTS'] + base_stats['REB']
            elif stat_type == 'AST+REB':
                return base_stats['AST'] + base_stats['REB']
            elif stat_type == 'PTS+AST+REB':
                return base_stats['PTS'] + base_stats['AST'] + base_stats['REB']

            return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar média de posição: {e}")
            return None
