// PlayerController - Handles player movement, camera, and interaction

import { Camera } from './Camera.js';
import { WeaponManager } from '../weapons/WeaponManager.js';
import InputManager from '../core/InputManager.js';

export class PlayerController {
    constructor(scene, physics, spawn) {
        this.scene = scene;
        this.physics = physics;
        this.spawn = spawn;

        // Create player body (capsule)
        this.mesh = BABYLON.MeshBuilder.CreateCapsule('player', {
            height: 1.8,
            radius: 0.35,
            capSubdivisions: 4,
            updatable: false
        }, this.scene);
        this.mesh.position = spawn.clone();
        this.mesh.checkCollisions = true;

        // Physics
        this.mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            this.mesh,
            BABYLON.PhysicsImpostor.CylinderImpostor,
            { mass: 1, friction: 0.5, restitution: 0 },
            this.scene
        );

        // Player properties
        this.health = 100;
        this.maxHealth = 100;
        this.team = 'BLUE';
        this.kills = 0;
        this.deaths = 0;
        this.isGrounded = false;
        this.isSprintMode = false;

        // Movement
        this.moveSpeed = 5.5;
        this.sprintSpeed = 9.0;
        this.jumpForce = 6;
        this.velocity = BABYLON.Vector3.Zero();
        this.wishDir = BABYLON.Vector3.Zero();

        // Camera
        this.camera = new Camera(scene, this.mesh);

        // Weapons
        this.weaponManager = new WeaponManager(this.scene, this.mesh, this.camera);

        // Input
        this.input = new InputManager();

        // Damage flash
        this.damageFlashAlpha = 0;
        this.damageFlashDuration = 0.2;
    }

    update(deltaTime) {
        // Handle input
        const movement = this.input.getMovementVector();
        const mouseDelta = this.input.getMouseDelta();

        // Update camera
        this.camera.update(mouseDelta);

        // Update sprint state
        this.isSprintMode = this.input.isKeyPressed('shift');

        // Apply movement
        this.applyMovement(movement, deltaTime);

        // Handle jump
        if (this.input.isKeyPressed('space') && this.isGrounded) {
            this.jump();
        }

        // Handle weapon fire
        if (this.input.mouse.down) {
            this.weaponManager.fire(this.camera.forward, this.mesh.position);
        }

        // Handle reload
        if (this.input.isKeyPressed('r')) {
            this.weaponManager.reload();
        }

        // Handle weapon switch (numbers 1-3)
        if (this.input.isKeyPressed('1')) this.weaponManager.selectWeapon(0);
        if (this.input.isKeyPressed('2')) this.weaponManager.selectWeapon(1);

        // Update weapons
        this.weaponManager.update(deltaTime);

        // Check if grounded
        this.checkGrounded();

        // Update damage flash
        this.damageFlashAlpha = Math.max(0, this.damageFlashAlpha - deltaTime / this.damageFlashDuration);

        // Respawn if fell off map
        if (this.mesh.position.y < -50) {
            this.respawn();
        }
    }

    applyMovement(movement, deltaTime) {
        // Get forward and right vectors from camera
        const forward = this.camera.forward;
        const right = this.camera.right;

        // Build wish direction
        this.wishDir = BABYLON.Vector3.Zero();
        this.wishDir.addInPlace(forward.scale(movement.z));
        this.wishDir.addInPlace(right.scale(movement.x));

        if (this.wishDir.length() > 0) {
            this.wishDir.normalize();
        }

        // Apply speed
        const currentSpeed = this.isSprintMode ? this.sprintSpeed : this.moveSpeed;

        // Accelerate towards wish direction (arcade-style, not physics-based)
        const targetVelocity = this.wishDir.scale(currentSpeed);
        targetVelocity.y = this.velocity.y; // Preserve vertical velocity (gravity)

        // Smooth acceleration
        this.velocity = BABYLON.Vector3.Lerp(this.velocity, targetVelocity, deltaTime * 8);

        // Apply velocity
        this.mesh.physicsImpostor.setLinearVelocity(this.velocity);
    }

    checkGrounded() {
        // Raycast downward
        const rayOrigin = this.mesh.position.clone();
        const rayDirection = BABYLON.Vector3.Down();
        const rayLength = 0.5;

        const raycastHit = new BABYLON.RaycastQuery(rayOrigin, rayDirection, rayLength);
        const hit = BABYLON.RayHelper.CreateAndShow(rayOrigin, rayDirection, rayLength, this.scene);

        this.isGrounded = false; // Simplified for now

        // Fall damage and respawn check
        if (this.mesh.position.y < -50) {
            this.takeDamage(100);
        }
    }

    jump() {
        if (!this.isGrounded) return;
        this.velocity.y = this.jumpForce;
        this.mesh.physicsImpostor.applyImpulse(
            BABYLON.Vector3.Up().scale(this.jumpForce * 10),
            this.mesh.getAbsolutePosition()
        );
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        this.damageFlashAlpha = 1;

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
    }

    kill() {
        this.kills++;
    }
}
