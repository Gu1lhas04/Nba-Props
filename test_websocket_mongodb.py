#!/usr/bin/env python
"""
Script de teste para verificar a instalação de WebSockets e MongoDB

Execute com: python test_websocket_mongodb.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Projeto_Apostas.settings')
django.setup()

from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mongodb_connection():
    """Testa conexão com MongoDB"""
    print("\n" + "="*50)
    print("TESTE 1: Conexão MongoDB")
    print("="*50)

    try:
        from Projeto_Apostas_App.mongodb_cache import nba_cache

        nba_cache.connect()
        print("✅ MongoDB conectado com sucesso!")
        print(f"   Host: {settings.MONGODB_SETTINGS['host']}")
        print(f"   Port: {settings.MONGODB_SETTINGS['port']}")
        print(f"   DB: {settings.MONGODB_SETTINGS['db']}")
        return True

    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")
        print("\n📝 Certifique-se de que:")
        print("   1. MongoDB está instalado: sudo apt-get install mongodb")
        print("   2. MongoDB está rodando: sudo systemctl start mongodb")
        print("   3. Variáveis no .env estão corretas")
        return False


def test_redis_connection():
    """Testa conexão com Redis"""
    print("\n" + "="*50)
    print("TESTE 2: Conexão Redis")
    print("="*50)

    try:
        import redis

        # Tenta conectar ao Redis
        r = redis.Redis(
            host=settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0][0],
            port=settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0][1],
            decode_responses=True
        )

        # Testa ping
        response = r.ping()

        if response:
            print("✅ Redis conectado com sucesso!")
            print(f"   Host: {settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0][0]}")
            print(f"   Port: {settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0][1]}")
            return True

    except Exception as e:
        print(f"❌ Erro ao conectar ao Redis: {e}")
        print("\n📝 Certifique-se de que:")
        print("   1. Redis está instalado: sudo apt-get install redis-server")
        print("   2. Redis está rodando: sudo systemctl start redis-server")
        print("   3. Teste manualmente: redis-cli ping")
        return False


def test_channels_installed():
    """Verifica se Django Channels está instalado"""
    print("\n" + "="*50)
    print("TESTE 3: Django Channels")
    print("="*50)

    try:
        import channels
        import daphne

        print("✅ Django Channels instalado!")
        print(f"   Versão Channels: {channels.__version__}")
        print(f"   ASGI Application: {settings.ASGI_APPLICATION}")
        return True

    except ImportError as e:
        print(f"❌ Django Channels não instalado: {e}")
        print("\n📝 Execute: pip install channels daphne")
        return False


def test_mongodb_cache_operations():
    """Testa operações básicas de cache"""
    print("\n" + "="*50)
    print("TESTE 4: Operações de Cache MongoDB")
    print("="*50)

    try:
        from Projeto_Apostas_App.mongodb_cache import nba_cache

        # Conecta
        nba_cache.connect()

        # Teste de escrita
        test_data = {
            'FIRST_NAME': 'Test',
            'LAST_NAME': 'Player',
            'TEAM_NAME': 'Test Team',
            'TEAM_ID': 1,
            'AGE': 25
        }

        success = nba_cache.set_player_info(999999, test_data)

        if not success:
            print("❌ Falha ao salvar no cache")
            return False

        # Teste de leitura
        cached_data = nba_cache.get_player_info(999999)

        if cached_data:
            print("✅ Operações de cache funcionando!")
            print(f"   Dados salvos e recuperados com sucesso")
            print(f"   Player: {cached_data['FIRST_NAME']} {cached_data['LAST_NAME']}")

            # Limpa dados de teste
            from Projeto_Apostas_App.mongodb_models import PlayerInfoCache
            PlayerInfoCache.objects(player_id=999999).delete()

            return True
        else:
            print("❌ Falha ao ler do cache")
            return False

    except Exception as e:
        print(f"❌ Erro nas operações de cache: {e}")
        return False


def test_websocket_routing():
    """Verifica se o routing WebSocket está configurado"""
    print("\n" + "="*50)
    print("TESTE 5: WebSocket Routing")
    print("="*50)

    try:
        from Projeto_Apostas_App import routing

        routes = routing.websocket_urlpatterns

        print("✅ WebSocket routing configurado!")
        print(f"   Total de rotas: {len(routes)}")

        for route in routes:
            print(f"   - {route.pattern}")

        return True

    except Exception as e:
        print(f"❌ Erro no routing: {e}")
        return False


def test_nba_api():
    """Testa se NBA API está funcionando"""
    print("\n" + "="*50)
    print("TESTE 6: NBA API")
    print("="*50)

    try:
        from nba_api.stats.static import players

        # Busca um jogador conhecido
        player_dict = players.get_players()

        if player_dict:
            print("✅ NBA API funcionando!")
            print(f"   Total de jogadores disponíveis: {len(player_dict)}")
            return True

    except Exception as e:
        print(f"❌ Erro ao acessar NBA API: {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "🏀"*25)
    print("TESTE DE INSTALAÇÃO - WebSockets & MongoDB")
    print("🏀"*25)

    results = {
        'MongoDB': test_mongodb_connection(),
        'Redis': test_redis_connection(),
        'Channels': test_channels_installed(),
        'Cache Operations': test_mongodb_cache_operations(),
        'WebSocket Routing': test_websocket_routing(),
        'NBA API': test_nba_api(),
    }

    # Resumo
    print("\n" + "="*50)
    print("RESUMO DOS TESTES")
    print("="*50)

    total = len(results)
    passed = sum(results.values())

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")

    print("="*50)
    print(f"Resultado: {passed}/{total} testes passaram")
    print("="*50)

    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        print("\n📝 Próximos passos:")
        print("   1. Inicie o servidor: daphne -b 0.0.0.0 -p 8000 Projeto_Apostas.asgi:application")
        print("   2. Acesse: http://localhost:8000")
        print("   3. WebSockets estarão funcionando automaticamente")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("\n📚 Consulte: WEBSOCKETS_MONGODB_SETUP.md")


if __name__ == '__main__':
    run_all_tests()
