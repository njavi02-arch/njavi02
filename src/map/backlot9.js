// Backlot-9 Map Data
// Small urban-industrial abandoned complex

import { BABYLON } from 'https://cdnjs.cloudflare.com/ajax/libs/babylonjs/7.0.0/babylon.min.js';

export const BACKLOT9_MAP = {
    name: 'BACKLOT-9',
    description: 'Small urban-industrial abandoned complex',

    terrain: {
        width: 100,
        height: 100
    },

    spawns: {
        BLUE: [
            new BABYLON.Vector3(-30, 2, -30),
            new BABYLON.Vector3(-25, 2, -25),
            new BABYLON.Vector3(-35, 2, -20)
        ],
        RED: [
            new BABYLON.Vector3(30, 2, 30),
            new BABYLON.Vector3(25, 2, 25),
            new BABYLON.Vector3(35, 2, 20)
        ]
    },

    structures: [
        // Central tower
        {
            name: 'central_tower',
            type: 'box',
            x: 0, y: 5, z: 0,
            width: 10, height: 15, depth: 10,
            material: { r: 0.3, g: 0.3, b: 0.3 }
        },

        // Left building
        {
            name: 'left_building',
            type: 'box',
            x: -25, y: 3, z: 0,
            width: 15, height: 8, depth: 20,
            material: { r: 0.4, g: 0.4, b: 0.4 }
        },

        // Right building
        {
            name: 'right_building',
            type: 'box',
            x: 25, y: 3, z: 0,
            width: 15, height: 8, depth: 20,
            material: { r: 0.4, g: 0.4, b: 0.4 }
        },

        // Front wall
        {
            name: 'front_wall',
            type: 'box',
            x: 0, y: 2, z: -30,
            width: 50, height: 4, depth: 2,
            material: { r: 0.5, g: 0.5, b: 0.5 }
        },

        // Back wall
        {
            name: 'back_wall',
            type: 'box',
            x: 0, y: 2, z: 30,
            width: 50, height: 4, depth: 2,
            material: { r: 0.5, g: 0.5, b: 0.5 }
        },

        // Left wall
        {
            name: 'left_wall',
            type: 'box',
            x: -40, y: 2, z: 0,
            width: 2, height: 4, depth: 50,
            material: { r: 0.5, g: 0.5, b: 0.5 }
        },

        // Right wall
        {
            name: 'right_wall',
            type: 'box',
            x: 40, y: 2, z: 0,
            width: 2, height: 4, depth: 50,
            material: { r: 0.5, g: 0.5, b: 0.5 }
        },

        // Obstacle 1
        {
            name: 'obstacle_1',
            type: 'box',
            x: -15, y: 2, z: -10,
            width: 8, height: 4, depth: 8,
            material: { r: 0.6, g: 0.6, b: 0.5 }
        },

        // Obstacle 2
        {
            name: 'obstacle_2',
            type: 'box',
            x: 15, y: 2, z: 10,
            width: 8, height: 4, depth: 8,
            material: { r: 0.6, g: 0.6, b: 0.5 }
        },

        // Pillar 1
        {
            name: 'pillar_1',
            type: 'cylinder',
            x: -10, y: 3, z: 0,
            diameter: 2, height: 10,
            material: { r: 0.7, g: 0.7, b: 0.7 }
        },

        // Pillar 2
        {
            name: 'pillar_2',
            type: 'cylinder',
            x: 10, y: 3, z: 0,
            diameter: 2, height: 10,
            material: { r: 0.7, g: 0.7, b: 0.7 }
        }
    ]
};
