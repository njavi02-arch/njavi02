// Weapon - Individual weapon class

export class Weapon {
    constructor(scene, config, name) {
        this.scene = scene;
        this.config = config;
        this.name = name;

        // Ammo
        this.magazine = config.magazineSize;
        this.reserve = config.maxReserveAmmo;

        // Fire rate
        this.timeSinceLastShot = 0;
        this.fireInterval = 1 / config.fireRate;
    }

    canFire() {
        return this.magazine > 0 && this.timeSinceLastShot >= this.fireInterval;
    }

    fire() {
        this.magazine--;
        this.timeSinceLastShot = 0;
    }

    reload() {
        const ammoNeeded = this.config.magazineSize - this.magazine;
        const ammoAvailable = Math.min(ammoNeeded, this.reserve);

        this.magazine += ammoAvailable;
        this.reserve -= ammoAvailable;
    }

    update(deltaTime) {
        this.timeSinceLastShot += deltaTime;
    }

    switchWeapon() {
        // Visual/animation handling for weapon switch would go here
    }
}
