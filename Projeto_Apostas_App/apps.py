from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ProjetoApostasAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Projeto_Apostas_App'

    def ready(self):
        """Chamado quando a aplicação está pronta"""
        # Importa e conecta ao MongoDB
        try:
            from .mongodb_cache import nba_cache
            nba_cache.connect()
            logger.info("✅ MongoDB conectado via AppConfig")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB não conectado: {e}")

        # Inicia os updaters de tempo real (apenas em produção/servidor ASGI)
        import os
        if os.environ.get('RUN_MAIN') or os.environ.get('DJANGO_ASGI'):
            try:
                from .realtime_updater import live_games_updater
                live_games_updater.start()
                logger.info("✅ Live Games Updater iniciado")
            except Exception as e:
                logger.warning(f"⚠️ Live Games Updater não iniciado: {e}")
