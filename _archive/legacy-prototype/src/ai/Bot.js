// Bot - AI-controlled bot

import { WeaponManager } from '../weapons/WeaponManager.js';

export class Bot {
    constructor(scene, physics, spawn, team) {
        this.scene = scene;
        this.physics = physics;
        this.spawn = spawn;
        this.team = team;

        // Create bot mesh (box for now)
        this.mesh = BABYLON.MeshBuilder.CreateCapsule('bot', {
            height: 1.8,
            radius: 0.35,
            capSubdivisions: 4
        }, this.scene);
        this.mesh.position = spawn.clone();

        // Physics
        this.mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            this.mesh,
            BABYLON.PhysicsImpostor.CylinderImpostor,
            { mass: 1, friction: 0.5, restitution: 0 },
            this.scene
        );

        // Bot properties
        this.health = 100;
        this.maxHealth = 100;
        this.kills = 0;
        this.deaths = 0;

        // AI behavior
        this.detectionRange = 50;
        this.target = null;
        this.state = 'IDLE'; // IDLE, PATROL, CHASE, FIRE
        this.stateTimer = 0;

        // Movement
        this.moveSpeed = 4.5;
        this.velocity = BABYLON.Vector3.Zero();

        // Weapon
        this.weaponManager = new WeaponManager(this.scene, this.mesh, this);
        this.fireTimer = 0;
    }

    update(deltaTime, player, allBots) {
        // Update AI behavior
        this.updateAI(player, allBots, deltaTime);

        // Update weapons
        this.weaponManager.update(deltaTime);

        // Movement
        if (this.state !== 'IDLE') {
            this.applyMovement(deltaTime);
        }

        // Respawn if fell off map
        if (this.mesh.position.y < -50) {
            this.respawn();
        }
    }

    updateAI(player, allBots, deltaTime) {
        // Simple AI: seek and attack player
        const distanceToPlayer = BABYLON.Vector3.Distance(this.mesh.position, player.mesh.position);

        if (distanceToPlayer < this.detectionRange) {
            this.state = 'CHASE';
            this.target = player;

            // Fire at player
            if (distanceToPlayer < 30) {
                const direction = player.mesh.position.subtract(this.mesh.position).normalize();
                this.weaponManager.fire(direction, this.mesh.position);
            }
        } else {
            this.state = 'PATROL';
            this.target = null;

            // Random patrol movement
            this.stateTimer += deltaTime;
            if (this.stateTimer > 5) {
                // Change direction randomly every 5 seconds
                this.stateTimer = 0;
            }
        }
    }

    applyMovement(deltaTime) {
        if (this.target) {
            // Move towards target
            const direction = this.target.mesh.position.subtract(this.mesh.position);
            direction.y = 0; // Don't fly
            if (direction.length() > 0) {
                direction.normalize();
                this.velocity = direction.scale(this.moveSpeed);
            }
        } else {
            // Patrol movement (random)
            const angle = Math.random() * Math.PI * 2;
            this.velocity = new BABYLON.Vector3(
                Math.cos(angle) * this.moveSpeed * 0.5,
                this.velocity.y,
                Math.sin(angle) * this.moveSpeed * 0.5
            );
        }

        // Apply gravity
        this.velocity.y -= 9.81 * deltaTime;

        // Apply velocity
        this.mesh.physicsImpostor.setLinearVelocity(this.velocity);
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        if (this.health <= 0) {
            this.die();
        }
    }

    die() {
        this.deaths++;
        this.respawn();
    }

    respawn() {
        this.health = this.maxHealth;
        this.mesh.position = this.spawn.clone();
        this.velocity = BABYLON.Vector3.Zero();
        this.target = null;
        this.state = 'IDLE';
    }

    kill() {
        this.kills++;
    }
}
