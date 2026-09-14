// WeaponManager - Manages player weapons and firing

import { Weapon } from './Weapon.js';
import { WEAPONS_CONFIG } from './weapons-config.js';

export class WeaponManager {
    constructor(scene, playerMesh, camera) {
        this.scene = scene;
        this.playerMesh = playerMesh;
        this.camera = camera;

        // Initialize weapons
        this.weapons = [];
        this.currentWeaponIndex = 0;

        this.weapons.push(new Weapon(this.scene, WEAPONS_CONFIG.BO01, 'BO-01'));
        this.weapons.push(new Weapon(this.scene, WEAPONS_CONFIG.BO41, 'BO-41'));

        // Weapon state
        this.isReloading = false;
        this.reloadTimeRemaining = 0;
    }

    getCurrentWeapon() {
        return this.weapons[this.currentWeaponIndex];
    }

    fire(direction, origin) {
        if (this.isReloading) return;

        const weapon = this.getCurrentWeapon();
        if (!weapon.canFire()) return;

        // Apply recoil
        const recoil = weapon.config.recoil;
        this.camera.pitch -= (Math.random() - 0.5) * recoil.vertical;
        this.camera.yaw += (Math.random() - 0.5) * recoil.horizontal;

        // Apply spread
        const spreadAngle = weapon.config.spread * (Math.random() + 0.5);
        const spread = new BABYLON.Vector3(
            (Math.random() - 0.5) * spreadAngle,
            (Math.random() - 0.5) * spreadAngle,
            0
        );

        const finalDirection = direction.add(spread).normalize();

        // Create bullet
        const bullet = BABYLON.MeshBuilder.CreateSphere('bullet', { diameter: 0.05 }, this.scene);
        bullet.position = origin.add(direction.scale(0.5));

        // Apply physics
        bullet.physicsImpostor = new BABYLON.PhysicsImpostor(
            bullet,
            BABYLON.PhysicsImpostor.SphereImpostor,
            { mass: 0.01, friction: 0, restitution: 0 },
            this.scene
        );

        // Velocity
        const bulletVelocity = finalDirection.scale(weapon.config.muzzleVelocity);
        bullet.physicsImpostor.setLinearVelocity(bulletVelocity);

        // Add metadata
        bullet.userData = {
            weapon: weapon,
            damage: weapon.config.damage,
            firedBy: this.playerMesh,
            lifetime: 5,
            isHit: false
        };

        // Muzzle flash
        this.createMuzzleFlash(origin, direction);

        // Fire sound
        this.playFireSound();

        // Update weapon
        weapon.fire();

        // Remove bullet after lifetime
        setTimeout(() => {
            if (bullet && bullet.dispose) {
                bullet.dispose();
            }
        }, weapon.config.range / weapon.config.muzzleVelocity * 1000 + 5000);
    }

    createMuzzleFlash(origin, direction) {
        // Create muzzle flash particle
        const flash = BABYLON.MeshBuilder.CreateSphere('flash', { diameter: 0.2 }, this.scene);
        flash.position = origin.add(direction.scale(0.3));

        const mat = new BABYLON.StandardMaterial('flashMat', this.scene);
        mat.emissiveColor = new BABYLON.Color3(1, 0.8, 0.3);
        mat.backFaceCulling = false;
        flash.material = mat;

        // Fade out
        let alpha = 1;
        const fadeInterval = setInterval(() => {
            alpha -= 0.2;
            mat.alpha = alpha;
            if (alpha <= 0) {
                clearInterval(fadeInterval);
                flash.dispose();
            }
        }, 10);
    }

    playFireSound() {
        // Audio feedback would go here
        // For now, we'll add a visual indicator on HUD
    }

    reload() {
        const weapon = this.getCurrentWeapon();
        if (this.isReloading || weapon.magazine === weapon.config.magazineSize) return;

        this.isReloading = true;
        this.reloadTimeRemaining = weapon.config.reloadTime;
    }

    selectWeapon(index) {
        if (index >= 0 && index < this.weapons.length && index !== this.currentWeaponIndex) {
            this.currentWeaponIndex = index;
            this.isReloading = false;
            this.reloadTimeRemaining = 0;
        }
    }

    update(deltaTime) {
        if (this.isReloading) {
            this.reloadTimeRemaining -= deltaTime;
            if (this.reloadTimeRemaining <= 0) {
                const weapon = this.getCurrentWeapon();
                weapon.reload();
                this.isReloading = false;
            }
        }

        // Update weapon state
        this.getCurrentWeapon().update(deltaTime);
    }

    getAmmoDisplay() {
        const weapon = this.getCurrentWeapon();
        return {
            magazine: weapon.magazine,
            reserve: weapon.reserve,
            magazineSize: weapon.config.magazineSize
        };
    }
}
