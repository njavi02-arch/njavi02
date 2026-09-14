// UIManager - Manages all UI/HUD elements

export class UIManager {
    constructor() {
        this.player = null;
        this.match = null;
    }

    initialize(player, match) {
        this.player = player;
        this.match = match;
    }

    update(player, match) {
        this.updateHealthDisplay(player);
        this.updateAmmoDisplay(player);
        this.updateScoreDisplay(match);
    }

    updateHealthDisplay(player) {
        const healthValue = document.getElementById('healthValue');
        const weaponName = document.getElementById('weaponName');

        if (healthValue) {
            healthValue.textContent = Math.ceil(player.health);
        }
        if (weaponName && player.weaponManager) {
            const weapon = player.weaponManager.getCurrentWeapon();
            weaponName.textContent = weapon.name;
        }
    }

    updateAmmoDisplay(player) {
        if (!player.weaponManager) return;

        const ammoMag = document.getElementById('ammoMag');
        const ammoReserve = document.getElementById('ammoReserve');
        const ammo = player.weaponManager.getAmmoDisplay();

        if (ammoMag) {
            ammoMag.textContent = ammo.magazine;
        }
        if (ammoReserve) {
            ammoReserve.textContent = ammo.reserve;
        }
    }

    updateScoreDisplay(match) {
        const scoreDisplay = document.getElementById('scoreDisplay');
        if (scoreDisplay) {
            const timeRemaining = Math.ceil(match.getTimeRemaining());
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            scoreDisplay.textContent = `BLUE ${match.blueScore} - RED ${match.redScore} | TIME ${timeStr}`;
        }
    }

    showEndScreen(winner) {
        // Create end screen
        const endScreen = document.createElement('div');
        endScreen.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
            color: #00ff00;
            text-align: center;
            font-size: 2rem;
            font-family: monospace;
        `;

        endScreen.innerHTML = `
            <div>
                <h1 style="font-size: 3rem; margin-bottom: 1rem;">${winner} TEAM WINS!</h1>
                <p style="margin-bottom: 2rem;">MATCH ENDED</p>
                <button onclick="location.reload()" style="padding: 1rem 2rem; background: #00ff00; color: #000; border: none; font-size: 1rem; cursor: pointer;">PLAY AGAIN</button>
            </div>
        `;

        document.body.appendChild(endScreen);
    }
}
