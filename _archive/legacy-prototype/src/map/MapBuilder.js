// MapBuilder - Constructs and manages game maps

export class MapBuilder {
    constructor(scene, physics) {
        this.scene = scene;
        this.physics = physics;
        this.spawns = {
            BLUE: [],
            RED: []
        };
    }

    async buildBacklot9() {
        // Import map data
        const mapData = await import('./backlot9.js').then(m => m.BACKLOT9_MAP);

        // Build terrain
        this.buildTerrain(mapData.terrain);

        // Build structures
        this.buildStructures(mapData.structures);

        // Setup spawns
        this.spawns = mapData.spawns;
    }

    buildTerrain(terrainData) {
        const ground = BABYLON.MeshBuilder.CreateGround(
            'ground',
            { width: 100, height: 100 },
            this.scene
        );

        const groundMaterial = new BABYLON.StandardMaterial('groundMat', this.scene);
        groundMaterial.diffuse = new BABYLON.Color3(0.4, 0.4, 0.4);
        ground.material = groundMaterial;

        // Physics for ground
        ground.physicsImpostor = new BABYLON.PhysicsImpostor(
            ground,
            BABYLON.PhysicsImpostor.BoxImpostor,
            { mass: 0, friction: 0.5 },
            this.scene
        );
    }

    buildStructures(structures) {
        for (const struct of structures) {
            this.buildStructure(struct);
        }
    }

    buildStructure(struct) {
        let mesh;

        switch (struct.type) {
            case 'box':
                mesh = BABYLON.MeshBuilder.CreateBox(struct.name, {
                    width: struct.width,
                    height: struct.height,
                    depth: struct.depth
                }, this.scene);
                break;

            case 'cylinder':
                mesh = BABYLON.MeshBuilder.CreateCylinder(struct.name, {
                    height: struct.height,
                    diameter: struct.diameter
                }, this.scene);
                break;

            default:
                return;
        }

        // Position and rotation
        mesh.position = new BABYLON.Vector3(struct.x, struct.y, struct.z);
        if (struct.rotation) {
            mesh.rotation = new BABYLON.Vector3(struct.rotation.x || 0, struct.rotation.y || 0, struct.rotation.z || 0);
        }

        // Material
        if (struct.material) {
            const mat = new BABYLON.StandardMaterial(struct.name + 'Mat', this.scene);
            mat.diffuse = new BABYLON.Color3(struct.material.r, struct.material.g, struct.material.b);
            mesh.material = mat;
        }

        // Physics
        if (struct.physics !== false) {
            mesh.physicsImpostor = new BABYLON.PhysicsImpostor(
                mesh,
                BABYLON.PhysicsImpostor.BoxImpostor,
                { mass: 0, friction: 0.5 },
                this.scene
            );
        }
    }

    getPlayerSpawn(team) {
        const spawns = this.spawns[team] || [];
        if (spawns.length === 0) {
            return new BABYLON.Vector3(0, 5, 0);
        }
        return spawns[Math.floor(Math.random() * spawns.length)].clone();
    }

    getBotSpawn(team) {
        return this.getPlayerSpawn(team);
    }
}
