// BULLET OPS - FPS Game Logic (Unified)
// All game systems in one file for Phase 1 prototype

const BABYLON = window.BABYLON;
const CANNON = window.CANNON;

// ========== WEAPONS CONFIG ==========
const WEAPONS_CONFIG = {
    BO01: {
        id: 'BO-01',
        name: 'BO-01 ASSAULT RIFLE',
        type: 'ASSAULT_RIFLE',
        damage: 24,
        fireRate: 10,
        magazineSize: 30,
        maxReserveAmmo: 120,
        reloadTime: 2.0,
        recoil: { vertical: 0.04, horizontal: 0.02 },
        spread: 0.02,
        muzzleVelocity: 900,
        range: 100,
        headshotMultiplier: 1.5
    },
    BO41: {
        id: 'BO-41',
        name: 'BO-41 PISTOL',
        type: 'PISTOL',
        damage: 35,
        fireRate: 6,
        magazineSize: 15,
        maxReserveAmmo: 60,
        reloadTime: 1.5,
        recoil: { vertical: 0.08, horizontal: 0.03 },
        spread: 0.03,
        muzzleVelocity: 400,
        range: 60,
        headshotMultiplier: 1.8
    }
};

// ========== INPUT MANAGER ==========
class InputManager {
    constructor() {
        this.keys = {};
        this.mouse = { x: 0, y: 0, deltaX: 0, deltaY: 0, down: false };
        this.isLocked = false;

        document.addEventListener('keydown', (e) => {
            this.keys[e.key.toLowerCase()] = true;
        });

        document.addEventListener('keyup', (e) => {
            this.keys[e.key.toLowerCase()] = false;
        });

        document.addEventListener('pointerlockchange', () => {
            this.isLocked = document.pointerLockElement === document.documentElement;
        });

        document.addEventListener('mousemove', (e) => {
            if (this.isLocked) {
                this.mouse.deltaX = e.movementX;
                this.mouse.deltaY = e.movementY;
            }
        });

        document.addEventListener('mousedown', (e) => {
            if (e.button === 0) {
                this.mouse.down = true;
                if (!this.isLocked) document.documentElement.requestPointerLock();
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 0) this.mouse.down = false;
        });
    }

    getMovement() {
        return {
            x: (this.keys['d'] ? 1 : 0) - (this.keys['a'] ? 1 : 0),
            z: (this.keys['w'] ? 1 : 0) - (this.keys['s'] ? 1 : 0)
        };
    }

    getMouseDelta() {
        const delta = { x: this.mouse.deltaX, y: this.mouse.deltaY };
        this.mouse.deltaX = 0;
        this.mouse.deltaY = 0;
        return delta;
    }

    isKeyDown(key) { return this.keys[key.toLowerCase()] || false; }
}

// ========== WEAPON CLASS ==========
class Weapon {
    constructor(config) {
        this.config = config;
        this.magazine = config.magazineSize;
        this.reserve = config.maxReserveAmmo;
        this.timeSinceLastShot = 0;
        this.fireInterval = 1 / config.fireRate;
        this.reloadTimeRemaining = 0;
        this.isReloading = false;
    }

    canFire() {
        return this.magazine > 0 && this.timeSinceLastShot >= this.fireInterval && !this.isReloading;
    }

    fire() {
        this.magazine--;
        this.timeSinceLastShot = 0;
    }

    reload() {
        if (this.magazine >= this.config.magazineSize) return;
        this.isReloading = true;
        this.reloadTimeRemaining = this.config.reloadTime;
    }

    update(deltaTime) {
        this.timeSinceLastShot += deltaTime;
        if (this.isReloading) {
            this.reloadTimeRemaining -= deltaTime;
            if (this.reloadTimeRemaining <= 0) {
                const needed = this.config.magazineSize - this.magazine;
                const available = Math.min(needed, this.reserve);
                this.magazine += available;
                this.reserve -= available;
                this.isReloading = false;
            }
        }
    }
}

// ========== CAMERA CLASS ==========
class FPSCamera {
    constructor(scene, parent) {
        this.scene = scene;
        this.camera = new BABYLON.UniversalCamera('playerCamera', new BABYLON.Vector3(0, 0.7, 0), scene);
        this.camera.parent = parent;
        this.camera.attachControl(scene.getEngine().getRenderingCanvas(), true);
        this.camera.inertia = 0.5;
        this.camera.keysUp = [];
        this.camera.keysDown = [];
        this.camera.keysLeft = [];
        this.camera.keysRight = [];

        this.pitch = 0;
        this.yaw = 0;
        this.sensitivity = 0.003;
    }

    update(mouseDelta) {
        this.yaw += mouseDelta.x * this.sensitivity;
        this.pitch -= mouseDelta.y * this.sensitivity;
        this.pitch = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.pitch));

        const euler = new BABYLON.Vector3(this.pitch, this.yaw, 0);
        this.camera.rotation = euler;
    }

    getForward() {
        const m = BABYLON.Matrix.RotationYawPitchRoll(this.yaw, this.pitch, 0);
        return BABYLON.Vector3.TransformCoordinates(BABYLON.Vector3.Forward(), m);
    }

    getRight() {
        const m = BABYLON.Matrix.RotationYawPitchRoll(this.yaw, this.pitch, 0);
        return BABYLON.Vector3.TransformCoordinates(BABYLON.Vector3.Right(), m);
    }
}

// ========== PLAYER CLASS ==========
class Player {
    constructor(scene, physics, spawn, team = 'BLUE') {
        this.scene = scene;
        this.physics = physics;
        this.spawn = spawn;
        this.team = team;

        // Create mesh
        this.mesh = BABYLON.MeshBuilder.CreateCapsule('player', {
            height: 1.8, radius: 0.35
        }, scene);
        this.mesh.position = spawn.clone();

        // Physics
        this.mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            this.mesh,
            BABYLON.PhysicsImpostor.CylinderImpostor,
            { mass: 1, friction: 0.5, restitution: 0 },
            scene
        );

        // Properties
        this.health = 100;
        this.maxHealth = 100;
        this.kills = 0;
        this.deaths = 0;
        this.isGrounded = true;
        this.velocity = BABYLON.Vector3.Zero();

        // Movement
        this.moveSpeed = 5.5;
        this.sprintSpeed = 9.0;
        this.jumpForce = 6;

        // Camera
        this.camera = new FPSCamera(scene, this.mesh);

        // Weapons
        this.weapons = [
            new Weapon(WEAPONS_CONFIG.BO01),
            new Weapon(WEAPONS_CONFIG.BO41)
        ];
        this.currentWeaponIndex = 0;

        // Input
        this.input = new InputManager();
    }

    getCurrentWeapon() {
        return this.weapons[this.currentWeaponIndex];
    }

    update(deltaTime, gameObjects = []) {
        // Input
        const movement = this.input.getMovement();
        const mouseDelta = this.input.getMouseDelta();
        const isSprinting = this.input.isKeyDown('shift');

        // Camera
        this.camera.update(mouseDelta);

        // Movement
        const forward = this.camera.getForward();
        const right = this.camera.getRight();

        let wishDir = new BABYLON.Vector3(0, 0, 0);
        wishDir.addInPlace(forward.scale(movement.z));
        wishDir.addInPlace(right.scale(movement.x));
        if (wishDir.length() > 0) wishDir.normalize();

        const speed = isSprinting ? this.sprintSpeed : this.moveSpeed;
        this.velocity.x = wishDir.x * speed;
        this.velocity.z = wishDir.z * speed;
        this.velocity.y -= 9.81 * deltaTime;

        this.mesh.physicsImpostor.setLinearVelocity(this.velocity);

        // Jump
        if (this.input.isKeyDown(' ') && this.isGrounded) {
            this.velocity.y = this.jumpForce;
            this.isGrounded = false;
        }

        // Shooting
        const weapon = this.getCurrentWeapon();
        if (this.input.mouse.down && weapon.canFire()) {
            this.fire(gameObjects);
        }

        // Reload
        if (this.input.isKeyDown('r')) {
            weapon.reload();
        }

        // Weapon switch
        if (this.input.isKeyDown('1')) this.currentWeaponIndex = 0;
        if (this.input.isKeyDown('2')) this.currentWeaponIndex = 1;

        // Update weapons
        for (let w of this.weapons) w.update(deltaTime);

        // Ground detection
        if (this.mesh.position.y < 2) {
            this.isGrounded = true;
            this.velocity.y = 0;
        } else {
            this.isGrounded = false;
        }

        // Respawn if fell
        if (this.mesh.position.y < -50) this.respawn();
    }

    fire(gameObjects) {
        const weapon = this.getCurrentWeapon();
        weapon.fire();

        const origin = this.mesh.position.add(new BABYLON.Vector3(0, 0.5, 0));
        const direction = this.camera.getForward();

        // Apply spread
        const spread = weapon.config.spread;
        const spreadDir = new BABYLON.Vector3(
            (Math.random() - 0.5) * spread,
            (Math.random() - 0.5) * spread,
            (Math.random() - 0.5) * spread
        );
        const finalDir = direction.add(spreadDir).normalize();

        // Create bullet
        const bullet = BABYLON.MeshBuilder.CreateSphere('bullet', { diameter: 0.05 }, this.scene);
        bullet.position = origin.add(finalDir.scale(0.5));
        bullet.physicsImpostor = new BABYLON.PhysicsImpostor(
            bullet,
            BABYLON.PhysicsImpostor.SphereImpostor,
            { mass: 0.01, friction: 0, restitution: 0 },
            this.scene
        );

        const bulletVel = finalDir.scale(weapon.config.muzzleVelocity);
        bullet.physicsImpostor.setLinearVelocity(bulletVel);

        bullet.userData = {
            damage: weapon.config.damage,
            firedBy: this,
            lifetime: 10
        };

        // Remove after lifetime
        setTimeout(() => bullet.dispose(), 10000);

        // Muzzle flash
        const flash = BABYLON.MeshBuilder.CreateSphere('flash', { diameter: 0.2 }, this.scene);
        flash.position = origin.add(finalDir.scale(0.3));
        const mat = new BABYLON.StandardMaterial('flashMat', this.scene);
        mat.emissiveColor = new BABYLON.Color3(1, 0.8, 0.3);
        flash.material = mat;
        setTimeout(() => flash.dispose(), 50);

        // Recoil
        this.camera.pitch -= (Math.random() - 0.5) * weapon.config.recoil.vertical;
        this.camera.yaw += (Math.random() - 0.5) * weapon.config.recoil.horizontal;
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        if (this.health <= 0) this.die();
    }

    die() {
        this.deaths++;
        this.respawn();
    }

    respawn() {
        this.health = this.maxHealth;
        this.mesh.position = this.spawn.clone();
        this.velocity = BABYLON.Vector3.Zero();
    }

    kill() {
        this.kills++;
    }
}

// ========== BOT CLASS ==========
class Bot {
    constructor(scene, physics, spawn, team = 'RED') {
        this.scene = scene;
        this.physics = physics;
        this.spawn = spawn;
        this.team = team;

        // Create mesh
        this.mesh = BABYLON.MeshBuilder.CreateCapsule('bot', {
            height: 1.8, radius: 0.35
        }, scene);
        this.mesh.position = spawn.clone();

        // Material (red color for RED team)
        const mat = new BABYLON.StandardMaterial('botMat', scene);
        mat.diffuse = team === 'RED' ? new BABYLON.Color3(1, 0, 0) : new BABYLON.Color3(0, 0, 1);
        this.mesh.material = mat;

        // Physics
        this.mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            this.mesh,
            BABYLON.PhysicsImpostor.CylinderImpostor,
            { mass: 1, friction: 0.5, restitution: 0 },
            scene
        );

        // Properties
        this.health = 100;
        this.maxHealth = 100;
        this.kills = 0;
        this.deaths = 0;
        this.team = team;
        this.velocity = BABYLON.Vector3.Zero();
        this.moveSpeed = 4.5;

        // AI
        this.target = null;
        this.state = 'PATROL';
        this.detectionRange = 50;
        this.stateTimer = 0;

        // Weapon
        this.weapon = new Weapon(WEAPONS_CONFIG.BO01);
        this.fireTimer = 0;
    }

    update(deltaTime, player, gameObjects) {
        // AI behavior
        const distToPlayer = BABYLON.Vector3.Distance(this.mesh.position, player.mesh.position);

        if (distToPlayer < this.detectionRange) {
            this.state = 'CHASE';
            this.target = player;

            // Fire
            if (distToPlayer < 30 && Math.random() < 0.1) {
                const dir = player.mesh.position.subtract(this.mesh.position).normalize();
                this.fire();
            }
        } else {
            this.state = 'PATROL';
        }

        // Movement
        if (this.target) {
            const dir = this.target.mesh.position.subtract(this.mesh.position);
            dir.y = 0;
            if (dir.length() > 0) {
                dir.normalize();
                this.velocity.x = dir.x * this.moveSpeed;
                this.velocity.z = dir.z * this.moveSpeed;
            }
        }

        // Gravity
        this.velocity.y -= 9.81 * deltaTime;
        this.mesh.physicsImpostor.setLinearVelocity(this.velocity);

        // Weapon update
        this.weapon.update(deltaTime);

        // Respawn if fell
        if (this.mesh.position.y < -50) this.respawn();
    }

    fire() {
        const weapon = this.weapon;
        if (!weapon.canFire()) return;

        weapon.fire();
        // Simplified - no visual for bot shots
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        if (this.health <= 0) this.die();
    }

    die() {
        this.deaths++;
        this.respawn();
    }

    respawn() {
        this.health = this.maxHealth;
        this.mesh.position = this.spawn.clone();
        this.velocity = BABYLON.Vector3.Zero();
    }

    kill() {
        this.kills++;
    }
}

// ========== GAME MANAGER ==========
class Game {
    constructor(engine) {
        this.engine = engine;
        this.scene = null;
        this.player = null;
        this.bots = [];
        this.gameActive = false;

        // Match data
        this.blueScore = 0;
        this.redScore = 0;
        this.timeLimit = 600;
        this.elapsedTime = 0;
    }

    async initialize() {
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.collisionsEnabled = true;
        this.scene.gravity = new BABYLON.Vector3(0, -9.81 * 2, 0);

        // Enable physics
        const physicsPlugin = new BABYLON.CannonJSPlugin(false, 10, CANNON);
        this.scene.enablePhysics(new BABYLON.Vector3(0, -9.81 * 2, 0), physicsPlugin);

        // Lighting
        const sun = new BABYLON.DirectionalLight('sun', new BABYLON.Vector3(-0.5, -1, -0.5), this.scene);
        sun.intensity = 0.9;

        const ambient = new BABYLON.HemisphericLight('ambient', new BABYLON.Vector3(0, 1, 0), this.scene);
        ambient.intensity = 0.6;

        // Build map
        this.buildMap();

        // Spawn player
        const playerSpawn = new BABYLON.Vector3(-20, 5, -20);
        this.player = new Player(this.scene, null, playerSpawn, 'BLUE');

        // Spawn bots
        const botSpawns = [
            new BABYLON.Vector3(20, 5, 20),
            new BABYLON.Vector3(25, 5, 25),
            new BABYLON.Vector3(30, 5, 20)
        ];

        for (let spawn of botSpawns) {
            this.bots.push(new Bot(this.scene, null, spawn, 'RED'));
        }

        this.gameActive = true;
    }

    buildMap() {
        // Ground
        const ground = BABYLON.MeshBuilder.CreateGround('ground', { width: 100, height: 100 }, this.scene);
        const groundMat = new BABYLON.StandardMaterial('groundMat', this.scene);
        groundMat.diffuse = new BABYLON.Color3(0.4, 0.4, 0.4);
        ground.material = groundMat;
        ground.physicsImpostor = new BABYLON.PhysicsImpostor(
            ground,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass: 0 },
            this.scene
        );

        // Central tower
        const tower = BABYLON.MeshBuilder.CreateBox('tower', { size: 10 }, this.scene);
        tower.position = new BABYLON.Vector3(0, 5, 0);
        const towerMat = new BABYLON.StandardMaterial('towerMat', this.scene);
        towerMat.diffuse = new BABYLON.Color3(0.5, 0.5, 0.5);
        tower.material = towerMat;
        tower.physicsImpostor = new BABYLON.PhysicsImpostor(
            tower,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass: 0 },
            this.scene
        );

        // Left building
        const leftBuilding = BABYLON.MeshBuilder.CreateBox('leftBuilding', { width: 15, height: 8, depth: 20 }, this.scene);
        leftBuilding.position = new BABYLON.Vector3(-25, 3, 0);
        leftBuilding.material = towerMat;
        leftBuilding.physicsImpostor = new BABYLON.PhysicsImpostor(
            leftBuilding,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass: 0 },
            this.scene
        );

        // Right building
        const rightBuilding = BABYLON.MeshBuilder.CreateBox('rightBuilding', { width: 15, height: 8, depth: 20 }, this.scene);
        rightBuilding.position = new BABYLON.Vector3(25, 3, 0);
        rightBuilding.material = towerMat;
        rightBuilding.physicsImpostor = new BABYLON.PhysicsImpostor(
            rightBuilding,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass: 0 },
            this.scene
        );

        // Obstacles
        for (let i = 0; i < 4; i++) {
            const obstacle = BABYLON.MeshBuilder.CreateBox(`obstacle_${i}`, { size: 5 }, this.scene);
            obstacle.position = new BABYLON.Vector3(
                (Math.random() - 0.5) * 60,
                2,
                (Math.random() - 0.5) * 60
            );
            obstacle.material = towerMat;
            obstacle.physicsImpostor = new BABYLON.PhysicsImpostor(
                obstacle,
                BABYLON.PhysicsImpostor.BoxImpostor,
                { mass: 0 },
                this.scene
            );
        }
    }

    update(deltaTime) {
        if (!this.gameActive) return;

        this.elapsedTime += deltaTime;

        // Update player
        this.player.update(deltaTime, this.bots);

        // Update bots
        for (let bot of this.bots) {
            bot.update(deltaTime, this.player, []);
        }

        // Update UI
        this.updateUI();

        // Check collisions with bullets
        this.checkCollisions();

        // Check win condition
        if (this.blueScore >= 10 || this.redScore >= 10 || this.elapsedTime >= this.timeLimit) {
            this.endGame();
        }
    }

    checkCollisions() {
        // Simplified bullet collision check
        // In full version would use raycasting or proper physics callbacks
    }

    updateUI() {
        document.getElementById('healthValue').textContent = Math.ceil(this.player.health);
        document.getElementById('ammoMag').textContent = this.player.getCurrentWeapon().magazine;
        document.getElementById('ammoReserve').textContent = this.player.getCurrentWeapon().reserve;
        document.getElementById('weaponName').textContent = this.player.getCurrentWeapon().config.name;

        const timeRemaining = Math.ceil(this.timeLimit - this.elapsedTime);
        const mins = Math.floor(timeRemaining / 60);
        const secs = timeRemaining % 60;
        document.getElementById('scoreDisplay').textContent =
            `BLUE ${this.blueScore} - RED ${this.redScore} | TIME ${mins}:${secs.toString().padStart(2, '0')}`;
    }

    endGame() {
        this.gameActive = false;
        const winner = this.blueScore > this.redScore ? 'BLUE' : 'RED';
        alert(`GAME OVER! ${winner} TEAM WINS!`);
        location.reload();
    }
}

// ========== MAIN ==========
document.getElementById('playButton')?.addEventListener('click', async () => {
    document.getElementById('mainMenu').classList.add('menu-hidden');
    document.getElementById('gameHUD').classList.remove('menu-hidden');

    const canvas = document.getElementById('renderCanvas');
    const engine = new BABYLON.Engine(canvas, true);

    const game = new Game(engine);
    await game.initialize();

    engine.runRenderLoop(() => {
        const deltaTime = engine.getDeltaTime() / 1000;
        game.update(deltaTime);
        game.scene.render();
    });

    window.addEventListener('resize', () => engine.resize());
});
