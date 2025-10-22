/**
 * Cliente WebSocket para atualizações em tempo real
 *
 * USO:
 * 1. Inclua este arquivo no seu template HTML
 * 2. Chame as funções apropriadas para conectar aos WebSockets
 *
 * EXEMPLOS:
 * - connectToLiveGames() - Para página de jogos ao vivo
 * - connectToPlayerStats(playerId) - Para página de detalhes do jogador
 * - connectToBetNotifications() - Para receber notificações de apostas
 */

// ==============================================
// LIVE GAMES WEBSOCKET
// ==============================================

let liveGamesSocket = null;

function connectToLiveGames() {
    // Determina o protocolo (ws ou wss)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live-games/`;

    console.log('🔗 Conectando ao WebSocket de jogos ao vivo...');

    liveGamesSocket = new WebSocket(wsUrl);

    liveGamesSocket.onopen = function(e) {
        console.log('✅ WebSocket de jogos ao vivo conectado');

        // Envia ping a cada 30 segundos para manter conexão ativa
        setInterval(() => {
            if (liveGamesSocket.readyState === WebSocket.OPEN) {
                liveGamesSocket.send(JSON.stringify({
                    type: 'ping'
                }));
            }
        }, 30000);
    };

    liveGamesSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'game_update') {
            console.log('🏀 Atualização de jogos recebida:', data.data);
            updateLiveGamesUI(data.data);
        }
    };

    liveGamesSocket.onerror = function(error) {
        console.error('❌ Erro no WebSocket:', error);
    };

    liveGamesSocket.onclose = function(e) {
        console.log('🔌 WebSocket desconectado. Tentando reconectar em 5s...');
        setTimeout(connectToLiveGames, 5000);
    };
}

function updateLiveGamesUI(data) {
    /**
     * Atualiza a UI com novos dados de jogos ao vivo
     *
     * CUSTOMIZAÇÃO:
     * Adapte esta função para atualizar os elementos da sua página
     */
    const games = data.games;
    const container = document.getElementById('live-games-container');

    if (!container) return;

    let html = '';

    games.forEach(game => {
        html += `
            <div class="game-card" data-game-id="${game.game_id}">
                <div class="game-header">
                    <span class="team">${game.away_team}</span>
                    <span class="score">${game.away_score}</span>
                </div>
                <div class="game-header">
                    <span class="team">${game.home_team}</span>
                    <span class="score">${game.home_score}</span>
                </div>
                <div class="game-info">
                    <span class="quarter">Q${game.quarter}</span>
                    <span class="time">${game.time_remaining}</span>
                    <span class="status ${game.status}">${game.game_status_text}</span>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    // Mostra timestamp da última atualização
    document.getElementById('last-update')?.textContent =
        `Última atualização: ${new Date(data.timestamp).toLocaleTimeString()}`;
}


// ==============================================
// PLAYER STATS WEBSOCKET
// ==============================================

let playerStatsSocket = null;

function connectToPlayerStats(playerId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/player-stats/${playerId}/`;

    console.log(`🔗 Conectando ao WebSocket do jogador ${playerId}...`);

    playerStatsSocket = new WebSocket(wsUrl);

    playerStatsSocket.onopen = function(e) {
        console.log('✅ WebSocket de stats do jogador conectado');

        // Ping keep-alive
        setInterval(() => {
            if (playerStatsSocket.readyState === WebSocket.OPEN) {
                playerStatsSocket.send(JSON.stringify({
                    type: 'ping'
                }));
            }
        }, 30000);
    };

    playerStatsSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'stats_update') {
            console.log('📊 Atualização de stats recebida:', data.data);
            updatePlayerStatsUI(data.data);
        }
    };

    playerStatsSocket.onerror = function(error) {
        console.error('❌ Erro no WebSocket:', error);
    };

    playerStatsSocket.onclose = function(e) {
        console.log('🔌 WebSocket desconectado');
    };
}

function updatePlayerStatsUI(data) {
    /**
     * Atualiza a UI com novas estatísticas do jogador
     *
     * CUSTOMIZAÇÃO:
     * Adapte para os elementos da sua página
     */
    if (data.points !== undefined) {
        document.getElementById('player-points')?.textContent = data.points;
    }
    if (data.assists !== undefined) {
        document.getElementById('player-assists')?.textContent = data.assists;
    }
    if (data.rebounds !== undefined) {
        document.getElementById('player-rebounds')?.textContent = data.rebounds;
    }
}


// ==============================================
// ODDS UPDATES WEBSOCKET
// ==============================================

let oddsSocket = null;

function connectToOdds() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/odds/`;

    console.log('🔗 Conectando ao WebSocket de odds...');

    oddsSocket = new WebSocket(wsUrl);

    oddsSocket.onopen = function(e) {
        console.log('✅ WebSocket de odds conectado');
    };

    oddsSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'odds_update') {
            console.log('💰 Atualização de odds recebida:', data.data);
            updateOddsUI(data.data);
        }
    };

    oddsSocket.onerror = function(error) {
        console.error('❌ Erro no WebSocket:', error);
    };

    oddsSocket.onclose = function(e) {
        console.log('🔌 WebSocket de odds desconectado');
        setTimeout(connectToOdds, 5000);
    };
}

function updateOddsUI(data) {
    /**
     * Atualiza odds na UI
     */
    const playerId = data.player_id;
    const statType = data.stat_type;
    const newOdd = data.odd;

    // Encontra o elemento da odd e atualiza
    const oddElement = document.querySelector(`[data-player="${playerId}"][data-stat="${statType}"] .odd-value`);

    if (oddElement) {
        const oldOdd = parseFloat(oddElement.textContent);
        oddElement.textContent = newOdd;

        // Adiciona efeito visual se a odd mudou
        if (newOdd > oldOdd) {
            oddElement.classList.add('odd-increased');
        } else if (newOdd < oldOdd) {
            oddElement.classList.add('odd-decreased');
        }

        setTimeout(() => {
            oddElement.classList.remove('odd-increased', 'odd-decreased');
        }, 2000);
    }
}


// ==============================================
// BET NOTIFICATIONS WEBSOCKET
// ==============================================

let betNotificationsSocket = null;

function connectToBetNotifications() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/bet-notifications/`;

    console.log('🔗 Conectando ao WebSocket de notificações...');

    betNotificationsSocket = new WebSocket(wsUrl);

    betNotificationsSocket.onopen = function(e) {
        console.log('✅ WebSocket de notificações conectado');
    };

    betNotificationsSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'bet_notification') {
            console.log('🔔 Notificação recebida:', data.data);
            showBetNotification(data.data);
        }
    };

    betNotificationsSocket.onerror = function(error) {
        console.error('❌ Erro no WebSocket:', error);
    };

    betNotificationsSocket.onclose = function(e) {
        console.log('🔌 WebSocket de notificações desconectado');
        setTimeout(connectToBetNotifications, 5000);
    };
}

function showBetNotification(data) {
    /**
     * Mostra notificação de aposta (ganha/perdida)
     */
    const notification = document.createElement('div');
    notification.className = `bet-notification ${data.status}`;

    let message = '';
    if (data.status === 'ganha') {
        message = `🎉 Sua aposta foi ganha! Ganhos: €${data.winnings}`;
    } else if (data.status === 'perdida') {
        message = `😔 Sua aposta foi perdida.`;
    }

    notification.innerHTML = `
        <div class="notification-content">
            <p>${message}</p>
            <small>${data.bet_description}</small>
        </div>
    `;

    document.body.appendChild(notification);

    // Remove após 5 segundos
    setTimeout(() => {
        notification.remove();
    }, 5000);

    // Atualiza saldo do usuário se disponível
    if (data.new_balance !== undefined) {
        document.getElementById('user-balance')?.textContent = `€${data.new_balance}`;
    }
}


// ==============================================
// UTILITY FUNCTIONS
// ==============================================

function disconnectAll() {
    /**
     * Desconecta todos os WebSockets
     */
    if (liveGamesSocket) liveGamesSocket.close();
    if (playerStatsSocket) playerStatsSocket.close();
    if (oddsSocket) oddsSocket.close();
    if (betNotificationsSocket) betNotificationsSocket.close();
}

// Limpa conexões quando a página é fechada
window.addEventListener('beforeunload', disconnectAll);
