// Weapons Configuration - All weapon stats and parameters

export const WEAPONS_CONFIG = {
    // BO-01 Assault Rifle
    BO01: {
        id: 'BO-01',
        name: 'BO-01 Assault Rifle',
        type: 'ASSAULT_RIFLE',
        damage: 24,
        fireRate: 10, // rounds per second
        magazineSize: 30,
        maxReserveAmmo: 120,
        reloadTime: 2.0, // seconds
        recoil: {
            vertical: 0.04,
            horizontal: 0.02
        },
        spread: 0.02,
        muzzleVelocity: 900,
        range: 100,
        headshotMultiplier: 1.5,
        ads: {
            enabled: true,
            fovMultiplier: 0.4
        },
        mobility: 85
    },

    // BO-41 Pistol
    BO41: {
        id: 'BO-41',
        name: 'BO-41 Pistol',
        type: 'PISTOL',
        damage: 35,
        fireRate: 6,
        magazineSize: 15,
        maxReserveAmmo: 60,
        reloadTime: 1.5,
        recoil: {
            vertical: 0.08,
            horizontal: 0.03
        },
        spread: 0.03,
        muzzleVelocity: 400,
        range: 60,
        headshotMultiplier: 1.8,
        ads: {
            enabled: true,
            fovMultiplier: 0.5
        },
        mobility: 100
    },

    // BO-11 SMG (placeholder)
    BO11: {
        id: 'BO-11',
        name: 'BO-11 SMG',
        type: 'SMG',
        damage: 16,
        fireRate: 15,
        magazineSize: 25,
        maxReserveAmmo: 150,
        reloadTime: 1.8,
        recoil: {
            vertical: 0.06,
            horizontal: 0.04
        },
        spread: 0.05,
        muzzleVelocity: 350,
        range: 50,
        headshotMultiplier: 1.3,
        ads: {
            enabled: true,
            fovMultiplier: 0.6
        },
        mobility: 110
    },

    // BO-21 Shotgun (placeholder)
    BO21: {
        id: 'BO-21',
        name: 'BO-21 Shotgun',
        type: 'SHOTGUN',
        damage: 80,
        fireRate: 2,
        magazineSize: 8,
        maxReserveAmmo: 32,
        reloadTime: 2.5,
        recoil: {
            vertical: 0.15,
            horizontal: 0.05
        },
        spread: 0.3,
        muzzleVelocity: 200,
        range: 30,
        headshotMultiplier: 1.2,
        ads: {
            enabled: false,
            fovMultiplier: 1.0
        },
        mobility: 70
    },

    // BO-31 Sniper (placeholder)
    BO31: {
        id: 'BO-31',
        name: 'BO-31 Sniper',
        type: 'SNIPER',
        damage: 90,
        fireRate: 1,
        magazineSize: 10,
        maxReserveAmmo: 40,
        reloadTime: 3.0,
        recoil: {
            vertical: 0.2,
            horizontal: 0.1
        },
        spread: 0.01,
        muzzleVelocity: 800,
        range: 300,
        headshotMultiplier: 2.0,
        ads: {
            enabled: true,
            fovMultiplier: 0.2
        },
        mobility: 50
    }
};
