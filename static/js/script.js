document.addEventListener('DOMContentLoaded', () => {
    const placeBetBtn = document.getElementById('place-bet');
    const hitBtn = document.getElementById('hit');
    const standBtn = document.getElementById('stand');
    const betInput = document.getElementById('bet-amount');
    const actionButtons = document.getElementById('action-buttons');
    const betArea = document.getElementById('bet-area');
    const messageElement = document.getElementById('message');
    const balanceElement = document.getElementById('balance');
    const playerHandElement = document.getElementById('player-hand');
    const dealerHandElement = document.getElementById('dealer-hand');
    const playerScoreElement = document.getElementById('player-score');
    const dealerScoreElement = document.getElementById('dealer-score');

    placeBetBtn.addEventListener('click', startGame);
    hitBtn.addEventListener('click', hit);
    standBtn.addEventListener('click', stand);

    async function startGame() {
        const bet = parseInt(betInput.value);
        const balance = parseInt(balanceElement.textContent);

        if (bet <= 0 || bet > balance) {
            messageElement.textContent = "Invalid bet amount!";
            return;
        }

        const response = await fetch('/api/start-game?bet=' + bet, {
            method: 'POST'
        });
        const gameState = await response.json();

        if (gameState.error) {
            messageElement.textContent = gameState.error;
            return;
        }

        updateGameState(gameState);
        betArea.style.display = 'none';
        actionButtons.style.display = 'block';
    }

    async function hit() {
        const response = await fetch('/api/hit', {
            method: 'POST'
        });
        const gameState = await response.json();
        
        if (gameState.error) {
            messageElement.textContent = gameState.error;
            return;
        }

        updateGameState(gameState);
    }

    async function stand() {
        const response = await fetch('/api/stand', {
            method: 'POST'
        });
        const gameState = await response.json();
        
        if (gameState.error) {
            messageElement.textContent = gameState.error;
            return;
        }

        updateGameState(gameState);
    }

    function updateGameState(gameState) {
        // Update hands
        playerHandElement.innerHTML = '';
        dealerHandElement.innerHTML = '';

        gameState.playerHand.forEach(card => {
            playerHandElement.appendChild(createCardElement(card));
        });

        gameState.dealerHand.forEach(card => {
            dealerHandElement.appendChild(createCardElement(card));
        });

        // Update scores
        playerScoreElement.textContent = gameState.playerScore;
        dealerScoreElement.textContent = gameState.dealerScore;

        // Update balance
        balanceElement.textContent = gameState.balance;

        // Update message
        messageElement.textContent = gameState.message;

        // Handle game over
        if (gameState.gameOver) {
            actionButtons.style.display = 'none';
            betArea.style.display = 'block';
        }
    }

    function createCardElement(card) {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        if (card.suit === '♥' || card.suit === '♦') {
            cardElement.className += ' red';
        }
        cardElement.textContent = card.rank + card.suit;
        return cardElement;
    }
});