# 🏀 NBA Best-Props

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socket.io&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

</div>

## 📋 Sobre o Projeto

O NBA Best-Props é uma plataforma sofisticada que combina análise de dados em tempo real, estatísticas avançadas e sistema de odds gratuito para fornecer insights valiosos sobre jogos da NBA. O sistema permite que utilizadores façam apostas informadas baseadas em análises estatísticas profundas com dados oficiais.

### 🎯 Objetivos

- Fornecer uma plataforma intuitiva para apostas em jogadores da NBA
- Implementar análises estatísticas avançadas de jogadores
- Apresentar as melhores apostas possíveis consoante os últimos 10 jogos
- **Sistema de odds 100% gratuito** baseado em dados oficiais da NBA
- **Atualizações em tempo real** via WebSockets
- Criar visualizações interativas e informativas
- Oferecer uma experiência de utilizador moderna e responsiva

## ✨ Funcionalidades Principais

### 🎲 Sistema de Apostas Inteligente
- **Odds Realistas**: Lines sempre terminando em .5 (padrão das casas de apostas)
- **Odds Variadas**: Baseadas na consistência real do jogador (entre 1.50 e 2.50)
- **Sistema de Cache**: MongoDB com TTL de 5 minutos para performance otimizada
- **Múltiplas Fontes**: Sistema de fallback automático (PrizePicks → NBA API)
- Histórico de apostas com gráficos de lucro/prejuízo
- Apostas em tempo real durante os jogos

### 📊 Análise Estatística Avançada
- **Múltiplas Temporadas**: Visualize estatísticas de temporadas anteriores (2020-21 até atual)
- **10+ Estatísticas Suportadas**: PTS, AST, REB, 3PT, BLK, STL, e combinações
- Análise de performance de jogadores com médias móveis
- Comparativos históricos e tendências de época
- Visualização de últimos 10 jogos
- Heatmaps e gráficos interativos com Plotly

### ⚡ Tempo Real e WebSockets
- **Live Games**: Atualizações automáticas a cada 10 segundos
- **Placar ao Vivo**: Score, quarter, tempo restante
- **Estatísticas ao Vivo**: Stats dos jogadores atualizadas em tempo real
- **Notificações**: Alertas de eventos importantes
- Django Channels + Redis para comunicação em tempo real

### 🗄️ Arquitetura Híbrida de Dados
- **PostgreSQL**: Dados persistentes (usuários, apostas, histórico)
- **MongoDB**: Cache de alta performance (stats, odds, live games)
- **Redis**: Message broker para WebSockets
- Sistema inteligente de cache com TTL configurável

### 🔮 Sistema de Odds Gratuito
- **100% Gratuito**: Substitui serviços pagos (Optimal Bet)
- **Dados Oficiais**: NBA API para precisão máxima
- **Lines Realistas**: Sempre terminam em .5 (24.5, 30.5, etc.)
- **Odds Calculadas**: Baseadas em probabilidade empírica e consistência
- **Margem da Casa**: Inclui vig de 5% (como casas reais)
- **10 Stats por Jogador**: PTS, AST, REB, 3PT, BLK, STL, combinações

### 📱 Interface Moderna
- Design responsivo e intuitivo
- Visualizações interativas com Plotly
- Dashboard personalizado por usuário
- Seletor de temporadas dinâmico
- Modo escuro/claro (futuro)

## 🛠️ Stack Tecnológica

### Backend
- **Framework**: Django 5.1.3
- **Linguagem**: Python 3.x
- **Bases de Dados**:
  - PostgreSQL (dados persistentes)
  - MongoDB (cache e dados temporários)
- **Real-time**:
  - Django Channels 4.0.0
  - Redis 5.0.1
  - Daphne 4.1.0
- **APIs**:
  - NBA API (dados oficiais)
  - PrizePicks API (odds - backup)
- **Processamento de Dados**: Pandas, NumPy
- **Visualização**: Plotly, Matplotlib
- **ODM**: MongoEngine 0.27.0

### Frontend
- **Design**:
  - Prototipagem e UI/UX no [Figma](https://www.figma.com/design/dfUqlcETMUqNOeiIZfczik/Projeto-Final?node-id=0-1&t=sWD2PcRY4ZpDET7P-1)

  ![Protótipo Figma](docs/images/prototipos.png)

- **HTML/CSS**: Desenvolvimento personalizado e responsivo
- **JavaScript**:
  - jQuery para interatividade
  - WebSocket client para atualizações em tempo real
  - AJAX para carregamento dinâmico de temporadas
- **Gráficos**: Plotly.js para visualizações dinâmicas
- **Templates**: Django Templates com estrutura modular

### DevOps
- **Versionamento**: Git
- **Servidor Local**: Django Development Server + Daphne
- **Túnel de Servidor**: Ngrok (para acesso remoto)
- **Gestão de Dependências**: pip + requirements.txt
- **Ambiente Virtual**: venv

## 🚀 Começando (Instalação Local)

### Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12 ou superior
- MongoDB 4.4 ou superior
- Redis 6.0 ou superior
- pip (gestor de pacotes Python)
- Git

### 🔧 Instalação

1. **Clone o Repositório**
```bash
git clone https://github.com/Gu1lhas04/Nba-Props.git
cd Nba-Props
```

2. **Configure o Ambiente Virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as Dependências**
```bash
pip install -r requirements.txt
```

4. **Configure os Serviços**

**PostgreSQL:**
```bash
# Crie uma base de dados PostgreSQL
createdb nba_betting
```

**MongoDB:**
```bash
# Inicie o serviço MongoDB
sudo systemctl start mongodb

# Ou no macOS
brew services start mongodb-community
```

**Redis:**
```bash
# Inicie o serviço Redis
sudo systemctl start redis

# Ou no macOS
brew services start redis
```

5. **Configure as Variáveis de Ambiente**
```bash
cp .env.example .env
# Edite o ficheiro .env com as suas configurações
```

6. **Execute as Migrações**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Crie um Superutilizador (opcional)**
```bash
python manage.py createsuperuser
```

8. **Teste o Sistema de Odds**
```bash
# Teste um jogador específico
python manage.py test_odds "Stephen Curry" PTS

# Pré-carregue cache de jogadores populares
python manage.py test_odds --refresh
```

9. **Inicie o Servidor**
```bash
# Servidor Django com suporte a WebSockets
python manage.py runserver

# Acesse: http://127.0.0.1:8000/
```

## 🔐 Variáveis de Ambiente

Crie um ficheiro `.env` na raiz do projeto:

```env
# Configurações Django
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DATABASE_URL=postgres://user:password@localhost:5432/nba_betting

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=nba_cache

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# NBA Cache Settings (opcional)
PLAYER_STATS_TTL=300  # 5 minutos
LIVE_GAMES_TTL=10     # 10 segundos
ODDS_CACHE_TTL=300    # 5 minutos
```

## 📊 Sistema de Odds

### Como Funciona

O sistema implementa um agregador de odds com fallback automático:

1. **Tenta PrizePicks API** (fonte primária)
2. **Fallback para NBA API** (dados oficiais - sempre funciona)
3. **Calcula odds realistas** baseadas em:
   - Média do jogador na temporada
   - Consistência (desvio padrão)
   - Probabilidade empírica de over/under
   - Margem da casa (5%)

### Características

- ✅ **Lines sempre em .5** (24.5, 30.5, etc.)
- ✅ **Odds variadas** (1.50 a 2.50)
- ✅ **100% Gratuito** (NBA API oficial)
- ✅ **Cache inteligente** (5 min TTL)
- ✅ **10 estatísticas** por jogador

### Exemplo de Uso

```python
from Projeto_Apostas_App.odds_integration import get_player_odds

# Busca odds de Stephen Curry
odds = get_player_odds("Stephen Curry", "PTS")

# Retorna:
# {
#   'line': 24.5,           # Sempre termina em .5
#   'over_odds': 1.96,      # Odds variadas
#   'under_odds': 1.85,     # Baseadas em dados reais
#   'source': 'StatisticalOddsProvider',
#   'cached': False
# }
```

## ⚡ WebSockets e Tempo Real

### Canais Disponíveis

1. **Live Games** (`ws://localhost:8000/ws/live_games/`)
   - Atualizações a cada 10 segundos
   - Score, quarter, tempo, estatísticas

2. **Player Stats** (`ws://localhost:8000/ws/player/{player_id}/`)
   - Stats do jogador em tempo real
   - Atualizações durante o jogo

3. **Game Details** (`ws://localhost:8000/ws/game/{game_id}/`)
   - Detalhes completos do jogo
   - Play-by-play

### Exemplo de Uso

```javascript
// Conectar ao WebSocket de jogos ao vivo
const socket = new WebSocket('ws://localhost:8000/ws/live_games/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Jogos ao vivo:', data.games);
    // Atualiza UI automaticamente
};
```

## 📷 Exemplos Visuais

### Interface Principal
![Interface Principal](docs/images/interface_principal.png)

### Análise de Jogadores
![Análise de Jogadores](docs/images/analise_jogadores.png)

### Gráfico de Performance
![Gráfico de Performance](docs/images/grafico_performance.png)

### Sistema de Previsão
![Sistema de Apostas](docs/images/sistema_previsao.png)

## 🚀 Deployment

### Acesso à Demonstração
A plataforma está disponível para demonstração através do Ngrok:
- **URL de Demonstração**: [Link da Demonstração](https://nbabestprops.ngrok.app)

### Para Aceder à Demonstração
1. Clique no link acima
2. Pode testar todas as funcionalidades sem necessidade de instalação local

### Notas Importantes
- A demonstração utiliza dados reais da NBA API
- As apostas são simuladas (não envolvem dinheiro real)
- WebSockets funcionam em tempo real
- Cache otimizado para melhor performance

## 🧪 Comandos Úteis

### Gestão de Odds
```bash
# Testar odds de um jogador
python manage.py test_odds "LeBron James" PTS

# Testar múltiplas stats
python manage.py test_odds "Stephen Curry" AST
python manage.py test_odds "Nikola Jokic" REB

# Pré-carregar cache (jogadores populares)
python manage.py test_odds --refresh
```

### Gestão de Cache
```bash
# Limpar cache MongoDB
python manage.py shell
>>> from Projeto_Apostas_App.mongodb_models import PlayerOddsCache
>>> PlayerOddsCache.objects.delete()
```

### Monitoramento
```bash
# Ver logs em tempo real
tail -f django.log

# Verificar conexões WebSocket
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
```

## 📈 Performance e Otimizações

### Sistema de Cache (3 Camadas)
1. **MongoDB Cache**
   - Player Stats: 5 min TTL
   - Live Games: 10 sec TTL
   - Odds: 5 min TTL

2. **Redis Cache**
   - Channel layers para WebSockets
   - Pub/Sub para broadcasting

3. **Application Cache**
   - Cache de templates Django
   - QuerySet caching

### Otimizações Implementadas
- ✅ Lazy loading de odds (apenas quando necessário)
- ✅ Paginação de resultados
- ✅ Índices MongoDB para queries rápidas
- ✅ Connection pooling PostgreSQL
- ✅ Compressão de dados WebSocket

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para a sua Feature (`git checkout -b feature/AmazingFeature`)
3. Commit das suas alterações (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código
- Siga o PEP 8 para código Python
- Realize comentários pertinentes no código
- Atualize a documentação quando necessário
- Teste novas features antes de submeter

## 📝 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✒️ Autores

* **Guilherme Silva** - *Desenvolvimento Full Stack* - [GitHub](https://github.com/Gu1lhas04)

## 🙏 Agradecimentos

- NBA API pela disponibilização de dados oficiais
- Comunidade Django e Django Channels
- Contribuidores do projeto

## 📞 Suporte

- Email: guilhermemsilva4@gmail.com
- Issues: [GitHub Issues](https://github.com/Gu1lhas04/Nba-Props/issues)

---

<div align="center">

**Desenvolvido com ❤️ por [Guilherme Silva](https://github.com/Gu1lhas04)**

⭐ Se este projeto te ajudou, considera dar uma estrela!

</div>
