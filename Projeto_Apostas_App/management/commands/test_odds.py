"""
Comando Django para testar o sistema de obtenção de odds

Uso:
    python manage.py test_odds "Stephen Curry" PTS
    python manage.py test_odds "LeBron James" AST
"""

from django.core.management.base import BaseCommand
from Projeto_Apostas_App.odds_integration import get_player_odds, refresh_popular_odds
from Projeto_Apostas_App.mongodb_cache import nba_cache
import json


class Command(BaseCommand):
    help = 'Testa o sistema de obtenção de odds'

    def add_arguments(self, parser):
        parser.add_argument(
            'player_name',
            type=str,
            nargs='?',
            default=None,
            help='Nome do jogador (opcional)'
        )
        parser.add_argument(
            'stat_type',
            type=str,
            nargs='?',
            default='PTS',
            help='Tipo de estatística (PTS, AST, REB, etc.)'
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Atualiza odds dos jogadores populares'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  TESTE DE SISTEMA DE ODDS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Conecta ao MongoDB
        try:
            nba_cache.connect()
            self.stdout.write(self.style.SUCCESS('✅ Conectado ao MongoDB'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao conectar ao MongoDB: {e}'))
            return

        # Se --refresh foi passado
        if options['refresh']:
            self.stdout.write(self.style.WARNING('\n🔄 Atualizando odds dos jogadores populares...'))
            count = refresh_popular_odds()
            self.stdout.write(self.style.SUCCESS(f'✅ {count} odds atualizadas\n'))
            return

        # Se nenhum jogador foi especificado, testa com exemplos
        if not options['player_name']:
            self.stdout.write(self.style.WARNING('\n📝 Nenhum jogador especificado. Testando com exemplos...\n'))
            test_players = [
                ('Stephen Curry', 'PTS'),
                ('LeBron James', 'AST'),
                ('Nikola Jokic', 'REB'),
            ]
        else:
            test_players = [(options['player_name'], options['stat_type'])]

        # Testa cada jogador
        for player_name, stat_type in test_players:
            self.stdout.write(self.style.HTTP_INFO(f'\n{"="*60}'))
            self.stdout.write(self.style.HTTP_INFO(f'Testando: {player_name} - {stat_type}'))
            self.stdout.write(self.style.HTTP_INFO(f'{"="*60}\n'))

            try:
                odds = get_player_odds(player_name, stat_type)

                if odds:
                    self.stdout.write(self.style.SUCCESS('✅ Odds obtidas com sucesso!\n'))
                    self.stdout.write(f"  Jogador: {player_name}")
                    self.stdout.write(f"  Estatística: {stat_type}")
                    self.stdout.write(f"  Linha: {odds.get('line', 0)}")
                    self.stdout.write(f"  Over Odds: {odds.get('over_odds', 0)}")
                    self.stdout.write(f"  Under Odds: {odds.get('under_odds', 0)}")
                    self.stdout.write(f"  Fonte: {odds.get('source', 'Unknown')}")
                    self.stdout.write(f"  Cached: {'Sim' if odds.get('cached') else 'Não'}")

                    # Mostra JSON formatado
                    self.stdout.write(self.style.WARNING('\nJSON:'))
                    self.stdout.write(json.dumps(odds, indent=2, default=str))
                else:
                    self.stdout.write(self.style.ERROR('❌ Nenhuma odd encontrada'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {e}'))
                import traceback
                self.stdout.write(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('  TESTE CONCLUÍDO'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
