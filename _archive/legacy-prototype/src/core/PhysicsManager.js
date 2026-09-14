// PhysicsManager - Wrapper around Babylon.js physics engine

export class PhysicsManager {
    constructor(scene) {
        this.scene = scene;
        this.plugin = new BABYLON.CannonJSPlugin(false, 10, CANNON);
        this.scene.enablePhysics(new BABYLON.Vector3(0, -9.81 * 2, 0), this.plugin);
    }

    createBoxCollider(mesh, mass = 0) {
        mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            mesh,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass, friction: 0.5, restitution: 0.1 },
            this.scene
        );
        return mesh.physicsImpostor;
    }

    createSphereCollider(mesh, mass = 0) {
        mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            mesh,
            BABYLON.PhysicsImpostor.SphereImpostor,
            { mass, friction: 0.5, restitution: 0.1 },
            this.scene
        );
        return mesh.physicsImpostor;
    }

    createCylinderCollider(mesh, mass = 0) {
        mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
            mesh,
            BABYLON.PhysicsImpostor.CylinderImpostor,
            { mass, friction: 0.5, restitution: 0.1 },
            this.scene
        );
        return mesh.physicsImpostor;
    }

    raycast(origin, direction, maxDistance = 1000) {
        const hit = BABYLON.PhysicsHelper.raycastQuery(
            this.scene,
            origin,
            direction,
            maxDistance,
            false
        );

        return hit.hasHit ? hit : null;
    }
}
