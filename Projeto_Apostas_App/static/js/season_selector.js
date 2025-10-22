/**
 * Sistema de seleção de temporadas para detalhes do jogador
 *
 * USO:
 * 1. Incluir este arquivo no template player_details.html
 * 2. Chamar initSeasonSelector(playerId) quando a página carregar
 */

let currentPlayerId = null;
let currentSeason = null;

/**
 * Inicializa o seletor de temporadas
 * @param {number} playerId - ID do jogador
 * @param {string} initialSeason - Temporada inicial (opcional)
 */
function initSeasonSelector(playerId, initialSeason = null) {
    console.log(`🏀 Inicializando seletor de temporadas para jogador ${playerId}, temporada inicial: ${initialSeason}`);

    currentPlayerId = playerId;
    currentSeason = initialSeason;

    // Carrega temporadas disponíveis
    loadAvailableSeasons(playerId);

    // Adiciona listener ao seletor de temporada
    const seasonSelect = document.getElementById('season-selector');
    if (seasonSelect) {
        console.log('✅ Dropdown encontrado, adicionando event listener');
        seasonSelect.addEventListener('change', function() {
            const selectedSeason = this.value;
            console.log(`📅 Temporada selecionada: ${selectedSeason}`);
            loadSeasonStats(playerId, selectedSeason);
        });
    } else {
        console.error('❌ Elemento #season-selector não encontrado!');
    }
}

/**
 * Carrega lista de temporadas disponíveis para o jogador
 * @param {number} playerId - ID do jogador
 */
async function loadAvailableSeasons(playerId) {
    try {
        showLoader('Carregando temporadas...');

        const response = await fetch(`/api/player/${playerId}/seasons/`);
        const data = await response.json();

        if (data.success && data.seasons && data.seasons.length > 0) {
            populateSeasonSelector(data.seasons, data.current_season);
            console.log(`✅ ${data.seasons.length} temporadas carregadas`);
        } else {
            console.warn('⚠️ Nenhuma temporada disponível');
        }

        hideLoader();
    } catch (error) {
        console.error('❌ Erro ao carregar temporadas:', error);
        hideLoader();
        showNotification('Erro ao carregar temporadas', 'error');
    }
}

/**
 * Popula o dropdown de seleção de temporada
 * @param {Array} seasons - Lista de temporadas
 * @param {string} currentSeason - Temporada atual
 */
function populateSeasonSelector(seasons, currentSeason) {
    const seasonSelect = document.getElementById('season-selector');

    if (!seasonSelect) {
        console.warn('⚠️ Elemento #season-selector não encontrado');
        return;
    }

    // Limpa opções existentes
    seasonSelect.innerHTML = '';

    // Adiciona opções de temporada
    seasons.forEach(season => {
        const option = document.createElement('option');
        option.value = season;
        option.textContent = formatSeasonDisplay(season);

        // Marca a temporada atual como selecionada
        if (season === currentSeason) {
            option.selected = true;
        }

        seasonSelect.appendChild(option);
    });

    // Mostra o seletor
    const seasonContainer = document.getElementById('season-selector-container');
    if (seasonContainer) {
        seasonContainer.style.display = 'block';
    }
}

/**
 * Carrega estatísticas de uma temporada específica
 * @param {number} playerId - ID do jogador
 * @param {string} season - Temporada no formato "2024-25"
 */
async function loadSeasonStats(playerId, season) {
    try {
        console.log(`🔄 Carregando stats: playerId=${playerId}, season=${season}`);
        showLoader(`Carregando temporada ${formatSeasonDisplay(season)}...`);

        const url = `/api/player/${playerId}/stats/?season=${season}`;
        console.log(`📡 Fazendo request para: ${url}`);

        const response = await fetch(url);
        console.log(`📥 Resposta recebida: status=${response.status}`);

        const data = await response.json();
        console.log('📦 Dados recebidos:', data);

        if (data.success) {
            console.log(`✅ Stats carregadas com sucesso para temporada ${season}`);
            updateStatsDisplay(data);
            currentSeason = season;
            showNotification(`Temporada ${formatSeasonDisplay(season)} carregada`, 'success');
        } else {
            console.error('❌ Erro na resposta:', data.error);
            showNotification(`Sem dados para temporada ${formatSeasonDisplay(season)}`, 'error');
        }

        hideLoader();
    } catch (error) {
        console.error('❌ Erro ao carregar stats:', error);
        hideLoader();
        showNotification('Erro ao carregar estatísticas', 'error');
    }
}

/**
 * Atualiza a exibição de estatísticas na página
 * @param {Object} data - Dados retornados da API
 */
function updateStatsDisplay(data) {
    // Atualiza médias
    const stats = data.stats || {};

    updateStatElement('player-points', stats.points);
    updateStatElement('player-assists', stats.assists);
    updateStatElement('player-rebounds', stats.rebounds);
    updateStatElement('player-3pt', stats.three_point);
    updateStatElement('player-blocks', stats.blocks);
    updateStatElement('player-steals', stats.steals);

    // Atualiza total de jogos
    const totalGamesElement = document.getElementById('total-games-display');
    if (totalGamesElement) {
        totalGamesElement.textContent = `Total de jogos: ${data.total_games || 0}`;
    }

    // Atualiza últimos 10 jogos
    if (data.last_10_games && data.last_10_games.length > 0) {
        updateLast10Games(data.last_10_games);
    }

    // Adiciona animação de atualização
    animateStatsUpdate();
}

/**
 * Atualiza valor de uma estatística específica
 * @param {string} elementId - ID do elemento HTML
 * @param {number} value - Valor da estatística
 */
function updateStatElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Adiciona efeito de transição
        element.classList.add('stat-updating');

        setTimeout(() => {
            element.textContent = value !== undefined && value !== null ? value.toFixed(1) : '0.0';
            element.classList.remove('stat-updating');
            element.classList.add('stat-updated');

            setTimeout(() => {
                element.classList.remove('stat-updated');
            }, 500);
        }, 200);
    }
}

/**
 * Atualiza tabela dos últimos 10 jogos
 * @param {Array} games - Lista de jogos
 */
function updateLast10Games(games) {
    const gamesContainer = document.getElementById('last-10-games-container');

    if (!gamesContainer) {
        console.warn('⚠️ Container de últimos 10 jogos não encontrado');
        return;
    }

    // Limpa container
    gamesContainer.innerHTML = '';

    // Adiciona jogos
    games.forEach(game => {
        const gameRow = document.createElement('div');
        gameRow.className = 'game-row';

        // Formata data
        const gameDate = new Date(game.GAME_DATE);
        const dateStr = gameDate.toLocaleDateString('pt-PT', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });

        gameRow.innerHTML = `
            <p class="game-cell">${dateStr}</p>
            <p class="game-cell">${game.MATCHUP || '-'}</p>
            <p class="game-cell">${game.MIN || 0}</p>
            <p class="game-cell">${game.PTS || 0}</p>
            <p class="game-cell">${game.AST || 0}</p>
            <p class="game-cell">${game.REB || 0}</p>
            <p class="game-cell">${game.FG3M || 0}</p>
            <p class="game-cell">${game.BLK || 0}</p>
            <p class="game-cell">${game.STL || 0}</p>
        `;

        gamesContainer.appendChild(gameRow);
    });
}

/**
 * Formata temporada para exibição
 * @param {string} season - Temporada no formato "2024-25"
 * @returns {string} - Temporada formatada "2024-2025"
 */
function formatSeasonDisplay(season) {
    if (!season) return '';

    const parts = season.split('-');
    if (parts.length !== 2) return season;

    const startYear = parts[0];
    const endYearShort = parts[1];

    // Converte 25 -> 2025
    const endYear = startYear.substring(0, 2) + endYearShort;

    return `${startYear}-${endYear}`;
}

/**
 * Adiciona animação ao atualizar stats
 */
function animateStatsUpdate() {
    const statsContainer = document.querySelector('.stats-container');
    if (statsContainer) {
        statsContainer.classList.add('stats-updating');
        setTimeout(() => {
            statsContainer.classList.remove('stats-updating');
        }, 600);
    }
}

/**
 * Mostra loader
 * @param {string} message - Mensagem do loader
 */
function showLoader(message = 'Carregando...') {
    let loader = document.getElementById('season-loader');

    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'season-loader';
        loader.className = 'season-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner"></div>
                <p class="loader-message">${message}</p>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        loader.querySelector('.loader-message').textContent = message;
    }

    loader.style.display = 'flex';
}

/**
 * Esconde loader
 */
function hideLoader() {
    const loader = document.getElementById('season-loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

/**
 * Mostra notificação
 * @param {string} message - Mensagem
 * @param {string} type - Tipo: 'success', 'error', 'info'
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `season-notification ${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
        <span class="notification-message">${message}</span>
    `;

    document.body.appendChild(notification);

    // Auto remove após 3 segundos
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}
