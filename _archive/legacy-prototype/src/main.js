// BULLET OPS - Main Entry Point

// Import Babylon dynamically
window.BABYLON = await import('babylonjs').then(m => m).catch(() => window.BABYLON);
await import('babylonjs-loaders');

import GameManager from './core/GameManager.js';

let gameManager = null;

// Initialize game
async function initializeGame() {
    const canvas = document.getElementById('renderCanvas');
    const engine = new BABYLON.Engine(canvas, true, {
        antialias: true,
        preferWebGL2: true,
        stencil: true
    });

    gameManager = new GameManager(engine);

    try {
        await gameManager.initialize();

        // Start render loop
        engine.runRenderLoop(() => {
            gameManager.update();
            gameManager.scene.render();
        });

        // Handle resize
        window.addEventListener('resize', () => {
            engine.resize();
        });

    } catch (error) {
        console.error('Game initialization error:', error);
    }
}

// Menu handling
document.getElementById('playButton')?.addEventListener('click', async () => {
    document.getElementById('mainMenu').classList.add('menu-hidden');
    document.getElementById('gameHUD').classList.remove('menu-hidden');

    if (!gameManager) {
        await initializeGame();
    }
});

document.getElementById('settingsButton')?.addEventListener('click', () => {
    alert('Settings coming soon!');
});

document.getElementById('quitButton')?.addEventListener('click', () => {
    alert('Thanks for playing BULLET OPS!');
});
