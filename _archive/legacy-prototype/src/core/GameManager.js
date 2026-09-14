// GameManager - Central coordinator for all game systems
// Manages scene, physics, player, bots, and match state

const BABYLON = window.BABYLON;

export default class GameManager {
    constructor(engine) {
        this.engine = engine;
        this.scene = null;
        this.camera = null;

        // Game systems
        this.physics = null;
        this.player = null;
        this.bots = null;
        this.match = null;
        this.ui = null;
        this.map = null;

        // Game state
        this.gameActive = false;
        this.deltaTime = 0;
        this.lastFrameTime = Date.now();
    }

    async initialize() {
        // Create scene
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.collisionsEnabled = true;
        this.scene.gravity = new BABYLON.Vector3(0, -9.81 * 2, 0); // 2x gravity for arcade feel
        this.scene.activeCameras = [];

        // Create physics system
        this.physics = new PhysicsManager(this.scene);

        // Build map
        this.map = new MapBuilder(this.scene, this.physics);
        await this.map.buildBacklot9();

        // Setup lighting
        this.setupLighting();

        // Initialize player
        const playerSpawn = this.map.getPlayerSpawn('BLUE');
        this.player = new PlayerController(this.scene, this.physics, playerSpawn);
        this.scene.activeCamera = this.player.camera.babylonCamera;

        // Initialize bots
        this.bots = new BotManager(this.scene, this.physics, this.map, this.player);
        this.bots.spawnBots(4, 'RED');

        // Initialize match
        this.match = new Match('TEAM_DEATHMATCH', {
            blueTeam: [this.player, ...this.bots.bots.filter(b => b.team === 'RED')],
            redTeam: this.bots.bots.filter(b => b.team === 'RED'),
            targetScore: 10,
            timeLimit: 600 // 10 minutes
        });

        // Initialize UI
        this.ui = new UIManager();
        this.ui.initialize(this.player, this.match);

        this.gameActive = true;
    }

    setupLighting() {
        // Main directional light (sun)
        const sun = new BABYLON.DirectionalLight('sun', new BABYLON.Vector3(-0.5, -1, -0.5), this.scene);
        sun.intensity = 0.9;
        sun.shadowMinZ = 0;
        sun.shadowMaxZ = 100;

        // Ambient light for fill
        const ambient = new BABYLON.HemisphericLight('ambient', new BABYLON.Vector3(0, 1, 0), this.scene);
        ambient.intensity = 0.6;

        // Rim light
        const rim = new BABYLON.PointLight('rim', new BABYLON.Vector3(0, 10, -20), this.scene);
        rim.intensity = 0.4;
        rim.range = 50;
    }

    update() {
        if (!this.gameActive) return;

        // Calculate delta time
        const now = Date.now();
        this.deltaTime = (now - this.lastFrameTime) / 1000;
        this.lastFrameTime = now;

        // Cap delta time to prevent large jumps
        const maxDeltaTime = 0.016 * 2; // ~30ms max
        const dt = Math.min(this.deltaTime, maxDeltaTime);

        // Update systems
        this.player.update(dt);
        this.bots.update(dt);
        this.match.update(dt);
        this.ui.update(this.player, this.match);

        // Check win condition
        if (this.match.checkWinCondition()) {
            this.endGame();
        }
    }

    endGame() {
        this.gameActive = false;
        this.ui.showEndScreen(this.match.getWinner());
    }
}
