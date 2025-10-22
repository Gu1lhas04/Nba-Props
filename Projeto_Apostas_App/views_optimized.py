"""
Exemplos de views otimizadas usando MongoDB cache e WebSockets

INSTRUÇÕES DE USO:
1. Substitua as views antigas pelas versões otimizadas deste arquivo
2. As views usam cache MongoDB automaticamente
3. Atualizam dados via WebSocket em tempo real
"""

from django.shortcuts import render
from django.http import JsonResponse
from .nba_cache_helpers import (
    get_cached_player_info,
    get_cached_player_stats,
    get_cached_live_games
)
import logging

logger = logging.getLogger(__name__)


def player_details_optimized(request, player_id):
    """
    View otimizada de detalhes do jogador usando cache MongoDB

    MUDANÇAS:
    - Usa cache MongoDB para reduzir chamadas à NBA API
    - Dados são atualizados automaticamente em background
    - Cache expira em 5 minutos (configurável)
    """
    try:
        # Busca informações do cache (ou API se não estiver no cache)
        player_info = get_cached_player_info(player_id)

        if not player_info:
            return render(request, 'error.html', {
                'message': 'Jogador não encontrado'
            })

        # Busca estatísticas do cache
        player_name = f"{player_info['FIRST_NAME']} {player_info['LAST_NAME']}"
        stats_data = get_cached_player_stats(player_id, player_name)

        if not stats_data:
            # Se não houver stats, retorna dados vazios
            stats_data = {
                'last_10_games': [],
                'averages': {
                    'points': 0,
                    'assists': 0,
                    'rebounds': 0,
                    'three_point': 0,
                    'blocks': 0,
                    'steals': 0,
                }
            }

        # Prepara dados para o template
        player_data = {
            'full_name': player_name,
            'age': player_info.get('AGE'),
            'height': player_info.get('HEIGHT'),
            'team_name': player_info.get('TEAM_NAME'),
            'team_id': player_info.get('TEAM_ID'),
            'last_10_games': stats_data['last_10_games'],
            'stats': stats_data['averages'],
            'player_id': player_id
        }

        return render(request, 'player_details.html', {
            'player': player_data,
            'use_websocket': True,  # Flag para ativar WebSocket no template
        })

    except Exception as e:
        logger.error(f"❌ Erro em player_details_optimized: {e}")
        return render(request, 'error.html', {
            'message': 'Erro ao carregar dados do jogador'
        })


def live_games_optimized(request):
    """
    View otimizada de jogos ao vivo usando cache MongoDB e WebSocket

    MUDANÇAS:
    - Dados vêm do cache MongoDB (atualizado a cada 10 segundos)
    - WebSocket atualiza a página automaticamente quando há mudanças
    - Muito mais rápido que chamar a API a cada requisição
    """
    try:
        # Busca jogos do cache
        games = get_cached_live_games()

        return render(request, 'live_games.html', {
            'games': games,
            'use_websocket': True,  # Ativa atualização em tempo real
        })

    except Exception as e:
        logger.error(f"❌ Erro em live_games_optimized: {e}")
        return render(request, 'error.html', {
            'message': 'Erro ao carregar jogos ao vivo'
        })


def api_live_games_json(request):
    """
    API endpoint JSON para jogos ao vivo
    Útil para chamadas AJAX do front-end
    """
    try:
        games = get_cached_live_games()

        return JsonResponse({
            'success': True,
            'games': games,
            'count': len(games)
        })

    except Exception as e:
        logger.error(f"❌ Erro em api_live_games_json: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def api_player_stats_json(request, player_id):
    """
    API endpoint JSON para estatísticas de jogador
    Útil para chamadas AJAX do front-end
    """
    try:
        player_info = get_cached_player_info(player_id)

        if not player_info:
            return JsonResponse({
                'success': False,
                'error': 'Jogador não encontrado'
            }, status=404)

        player_name = f"{player_info['FIRST_NAME']} {player_info['LAST_NAME']}"
        stats_data = get_cached_player_stats(player_id, player_name)

        return JsonResponse({
            'success': True,
            'player_id': player_id,
            'player_name': player_name,
            'stats': stats_data
        })

    except Exception as e:
        logger.error(f"❌ Erro em api_player_stats_json: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
