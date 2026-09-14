// Camera - FPS camera system

export class Camera {
    constructor(scene, playerMesh) {
        this.scene = scene;
        this.playerMesh = playerMesh;

        // Create camera
        this.babylonCamera = new BABYLON.UniversalCamera('playerCamera', new BABYLON.Vector3(0, 0.7, 0), this.scene);
        this.babylonCamera.parent = playerMesh;
        this.babylonCamera.attachControl(this.scene.getEngine().getRenderingCanvas(), true);

        // Camera settings
        this.babylonCamera.inertia = 0.5;
        this.babylonCamera.angularSensibility = 1000;
        this.babylonCamera.keysUp = [];
        this.babylonCamera.keysDown = [];
        this.babylonCamera.keysLeft = [];
        this.babylonCamera.keysRight = [];
        this.babylonCamera.checkCollisions = false;

        // Euler angles
        this.pitch = 0; // up/down
        this.yaw = 0;   // left/right

        // Direction vectors
        this.forward = BABYLON.Vector3.Forward();
        this.right = BABYLON.Vector3.Right();
        this.up = BABYLON.Vector3.Up();

        // Mouse sensitivity
        this.sensitivity = 0.003;

        // FOV
        this.fov = 75;
        this.babylonCamera.fov = this.fov / 180 * Math.PI;
    }

    update(mouseDelta) {
        // Update angles based on mouse movement
        this.yaw += mouseDelta.x * this.sensitivity;
        this.pitch -= mouseDelta.y * this.sensitivity;

        // Clamp pitch
        this.pitch = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.pitch));

        // Create rotation matrix
        const pitchAxis = BABYLON.Axis.X;
        const yawAxis = BABYLON.Axis.Y;

        const pitchQuat = BABYLON.Quaternion.RotationAxis(pitchAxis, this.pitch);
        const yawQuat = BABYLON.Quaternion.RotationAxis(yawAxis, this.yaw);

        const totalQuat = yawQuat.multiply(pitchQuat);

        // Update direction vectors
        this.forward = BABYLON.Vector3.TransformCoordinates(
            BABYLON.Vector3.Forward(),
            BABYLON.Matrix.RotationQuaternionToRef(totalQuat, new BABYLON.Matrix())
        );

        this.right = BABYLON.Vector3.TransformCoordinates(
            BABYLON.Vector3.Right(),
            BABYLON.Matrix.RotationQuaternionToRef(totalQuat, new BABYLON.Matrix())
        );

        this.up = BABYLON.Vector3.Up();

        // Update camera rotation
        this.babylonCamera.rotation = totalQuat.toEulerAngles();
    }

    getViewMatrix() {
        return this.babylonCamera.getViewMatrix();
    }
}
