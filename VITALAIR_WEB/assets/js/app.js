/* ============================================
   VITALAIR - APP.JS
   ============================================ */

// ============================================
// CARRITO
// ============================================

class VitalAirCart {
    constructor() {
        this.items = this.loadCart();
        this.updateCartUI();
    }

    loadCart() {
        const saved = localStorage.getItem('vitalair_cart');
        return saved ? JSON.parse(saved) : [];
    }

    saveCart() {
        localStorage.setItem('vitalair_cart', JSON.stringify(this.items));
        this.updateCartUI();
    }

    addItem(product) {
        const existing = this.items.find(item =>
            item.id === product.id && item.flavor === product.flavor
        );

        if (existing) {
            existing.quantity += product.quantity || 1;
        } else {
            this.items.push({
                ...product,
                quantity: product.quantity || 1
            });
        }

        this.saveCart();
        this.showNotification(`${product.name} agregado al carrito`);
    }

    removeItem(index) {
        this.items.splice(index, 1);
        this.saveCart();
    }

    updateQuantity(index, quantity) {
        if (quantity <= 0) {
            this.removeItem(index);
        } else {
            this.items[index].quantity = quantity;
            this.saveCart();
        }
    }

    updateCartUI() {
        const count = this.items.reduce((sum, item) => sum + item.quantity, 0);
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    getTotalPrice() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    getTotalItems() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    }

    clear() {
        this.items = [];
        this.saveCart();
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Inicializar carrito global
const cart = new VitalAirCart();

// ============================================
// NAVEGACIÓN
// ============================================

function initNavigation() {
    const navLinks = document.querySelectorAll('nav a');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });

    // Cart click
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.addEventListener('click', () => {
            window.location.href = 'pages/carrito.html';
        });
    }
}

// ============================================
// PRODUCTOS
// ============================================

const PRODUCTS = {
    basico: {
        id: 'basico',
        name: 'VitalAir Básico',
        price: 19.99,
        originalPrice: 29.99,
        rating: 4.7,
        reviews: 45,
        description: 'Tu primer paso hacia una respiración diferente',
        fullDescription: 'La perfecta introducción a la tecnología inteligente. Diseñado para quienes descubren por primera vez cómo la inhalación consciente puede transformar tu bienestar diario.',
        specs: [
            'Tecnología de inhalación inteligente con sensor de flujo',
            '120 inhalaciones por recarga',
            'Pantalla LED minimalista',
            'Batería de 8 horas',
            'Diseño compacto (85g)',
            'Compatible con 13 sabores'
        ],
        features: [
            'Sensor de flujo',
            'Control simple',
            'LED display'
        ],
        badge: 'BÁSICO'
    },
    premium: {
        id: 'premium',
        name: 'VitalAir Premium',
        price: 49.99,
        originalPrice: 69.99,
        rating: 4.9,
        reviews: 128,
        description: 'La opción más elegida por usuarios regulares',
        fullDescription: 'El equilibrio perfecto entre potencia y precisión. Diseñado para quienes integran la inhalación consciente en su rutina diaria.',
        specs: [
            'Tecnología inteligente dual: sensor de flujo + control de temperatura',
            '300 inhalaciones por recarga',
            'Pantalla LCD con información en tiempo real',
            'Batería de 16 horas',
            'Carga rápida (45 minutos)',
            'Control de intensidad en 3 niveles'
        ],
        features: [
            'Dual sensors',
            'Temperature control',
            'LCD display',
            '3 intensity levels'
        ],
        badge: 'MÁS ELEGIDO'
    },
    pro: {
        id: 'pro',
        name: 'VitalAir Pro',
        price: 89.99,
        originalPrice: 129.99,
        rating: 4.9,
        reviews: 89,
        description: 'Para quienes exigen lo mejor',
        fullDescription: 'La cúspide de nuestra tecnología. Diseñado para usuarios que demandan máximo control, máxima autonomía y la experiencia más refinada posible.',
        specs: [
            'Tecnología inteligente triple: sensor + temperatura + patrones',
            '500 inhalaciones por recarga',
            'Pantalla OLED full color',
            'Batería de 24 horas',
            'Carga ultra rápida (20 minutos)',
            'Control de intensidad en 7 niveles',
            'Resistencia IPX4'
        ],
        features: [
            'Triple sensors',
            'OLED display',
            '7 intensity levels',
            'IPX4 resistant',
            '24h battery'
        ],
        badge: 'PREMIUM'
    }
};

const FLAVORS = [
    { id: 'mango', name: 'Mango', desc: 'Tropical, energizante', color: '#FFA500' },
    { id: 'mint', name: 'Mint', desc: 'Refrescante, mentolado', color: '#4DB6AC' },
    { id: 'strawberry', name: 'Strawberry', desc: 'Suave, frutal', color: '#FF6B6B' },
    { id: 'blueberry', name: 'Blueberry', desc: 'Profundo, premium', color: '#7B68A6' },
    { id: 'raspberry', name: 'Raspberry', desc: 'Intenso, sofisticado', color: '#E91E63' },
    { id: 'coffee', name: 'Coffee', desc: 'Concentrado, tonificante', color: '#6D5344' },
    { id: 'cinnamon', name: 'Cinnamon', desc: 'Cálido, especiado', color: '#A86845' },
    { id: 'maple-pepper', name: 'Maple Pepper', desc: 'Único, sofisticado', color: '#C55A4F' },
    { id: 'orange', name: 'Orange', desc: 'Cítrico, energético', color: '#F5A623' },
    { id: 'lemon', name: 'Lemon', desc: 'Limpio, vivificante', color: '#FFD700' },
    { id: 'grapefruit', name: 'Grapefruit', desc: 'Amargo, refinado', color: '#FF9AA2' },
    { id: 'cranberry', name: 'Cranberry', desc: 'Tónico, elegante', color: '#C41E3A' },
    { id: 'vanilla', name: 'Vanilla', desc: 'Clásico, versátil', color: '#D4C5B0' }
];

// ============================================
// UTILIDADES
// ============================================

function formatPrice(price) {
    return `€${price.toFixed(2)}`;
}

function renderStars(rating) {
    const stars = Math.round(rating);
    let html = '';
    for (let i = 0; i < 5; i++) {
        html += i < stars ? '★' : '☆';
    }
    return html;
}

function createProductCard(productId) {
    const product = PRODUCTS[productId];
    return `
        <div class="card fade-in">
            <div class="card-badge">${product.badge}</div>
            <h3 class="card-title">${product.name}</h3>
            <div style="margin-bottom: 12px; font-size: 13px; color: #999;">
                ${renderStars(product.rating)} ${product.rating}/5 (${product.reviews} reviews)
            </div>
            <p class="card-description">${product.description}</p>
            <div class="flex-between mb-3">
                <div>
                    <div class="card-price">${formatPrice(product.price)}</div>
                    <div style="font-size: 12px; color: #999; text-decoration: line-through;">
                        ${formatPrice(product.originalPrice)}
                    </div>
                </div>
            </div>
            <button class="btn btn-primary btn-large" onclick="window.location.href='pages/productos.html?id=${productId}'">
                Ver detalles
            </button>
        </div>
    `;
}

// ============================================
// INIT
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
});
