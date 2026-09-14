// Match - Manages game match state and scoring

export class Match {
    constructor(gameMode, config) {
        this.gameMode = gameMode;
        this.config = config;

        // Teams
        this.blueTeam = config.blueTeam || [];
        this.redTeam = config.redTeam || [];

        // Scoring
        this.blueScore = 0;
        this.redScore = 0;
        this.targetScore = config.targetScore || 10;

        // Time
        this.elapsedTime = 0;
        this.timeLimit = config.timeLimit || 600; // 10 minutes

        // Game state
        this.isActive = true;
        this.winner = null;
    }

    update(deltaTime) {
        if (!this.isActive) return;

        // Update time
        this.elapsedTime += deltaTime;

        // Check time limit
        if (this.elapsedTime >= this.timeLimit) {
            this.isActive = false;
        }
    }

    awardKill(killer, victim) {
        killer.kill();

        if (killer.team === 'BLUE') {
            this.blueScore++;
        } else {
            this.redScore++;
        }
    }

    checkWinCondition() {
        if (this.blueScore >= this.targetScore) {
            this.winner = 'BLUE';
            this.isActive = false;
            return true;
        }
        if (this.redScore >= this.targetScore) {
            this.winner = 'RED';
            this.isActive = false;
            return true;
        }
        return false;
    }

    getTimeRemaining() {
        return Math.max(0, this.timeLimit - this.elapsedTime);
    }

    getWinner() {
        return this.winner;
    }

    getScoreboard() {
        return {
            blue: this.blueScore,
            red: this.redScore,
            timeRemaining: this.getTimeRemaining()
        };
    }
}
