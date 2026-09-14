// BotManager - Manages all bots in the game

import { Bot } from './Bot.js';

export class BotManager {
    constructor(scene, physics, map, player) {
        this.scene = scene;
        this.physics = physics;
        this.map = map;
        this.player = player;
        this.bots = [];
    }

    spawnBots(count, team) {
        for (let i = 0; i < count; i++) {
            const spawn = this.map.getBotSpawn(team);
            const bot = new Bot(this.scene, this.physics, spawn, team);
            this.bots.push(bot);
        }
    }

    update(deltaTime) {
        for (const bot of this.bots) {
            bot.update(deltaTime, this.player, this.bots);

            // Check if bot died
            if (bot.health <= 0) {
                // Handle bot death and respawn
                setTimeout(() => {
                    bot.respawn();
                }, 2000);
            }
        }
    }

    getBotByIndex(index) {
        return this.bots[index];
    }

    removeBotByIndex(index) {
        if (this.bots[index]) {
            this.bots[index].mesh.dispose();
            this.bots.splice(index, 1);
        }
    }
}
