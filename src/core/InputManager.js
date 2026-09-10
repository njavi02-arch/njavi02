// InputManager - Handles keyboard and mouse input

export default class InputManager {
    constructor() {
        this.keys = {
            'w': false,
            'a': false,
            's': false,
            'd': false,
            'shift': false,
            'space': false,
            'ctrl': false
        };

        this.mouse = {
            x: 0,
            y: 0,
            deltaX: 0,
            deltaY: 0,
            down: false
        };

        this.isLocked = false;

        this.setupKeyboardListeners();
        this.setupMouseListeners();
    }

    setupKeyboardListeners() {
        window.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (this.keys.hasOwnProperty(key)) {
                this.keys[key] = true;
            }
            if (key === 'shift') this.keys['shift'] = true;
            if (key === 'control') this.keys['ctrl'] = true;
            if (key === ' ') this.keys['space'] = true;
        });

        window.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            if (this.keys.hasOwnProperty(key)) {
                this.keys[key] = false;
            }
            if (key === 'shift') this.keys['shift'] = false;
            if (key === 'control') this.keys['ctrl'] = false;
            if (key === ' ') this.keys['space'] = false;
        });
    }

    setupMouseListeners() {
        document.addEventListener('pointerlockchange', () => {
            this.isLocked = document.pointerLockElement === document.documentElement;
        });

        document.addEventListener('mousemove', (e) => {
            if (this.isLocked) {
                this.mouse.deltaX = e.movementX;
                this.mouse.deltaY = e.movementY;
            }
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        document.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left click
                this.mouse.down = true;
                if (!this.isLocked) {
                    document.documentElement.requestPointerLock();
                }
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (e.button === 0) {
                this.mouse.down = false;
            }
        });
    }

    isKeyPressed(key) {
        return this.keys[key.toLowerCase()] || false;
    }

    getMovementVector() {
        const x = (this.keys['d'] ? 1 : 0) - (this.keys['a'] ? 1 : 0);
        const z = (this.keys['w'] ? 1 : 0) - (this.keys['s'] ? 1 : 0);
        return { x, z };
    }

    getMouseDelta() {
        const delta = {
            x: this.mouse.deltaX,
            y: this.mouse.deltaY
        };
        this.mouse.deltaX = 0;
        this.mouse.deltaY = 0;
        return delta;
    }

    getMouseSensitivity() {
        return 0.003; // Radians per pixel
    }
}
