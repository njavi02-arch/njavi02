/*
 * Datos de reseñas — separados del código principal a propósito.
 *
 * Este archivo es la única fuente de datos del carrusel de valoraciones.
 * Hoy contiene reseñas de EJEMPLO (ver disclaimer en la sección de reviews
 * del sitio). Para conectar reseñas reales, reemplazá el array VDT_REVIEWS
 * por los datos de tu proveedor (app de reviews de Shopify como Judge.me /
 * Loox, o tu propia base de datos) manteniendo esta misma forma:
 *
 *   { name, initials, rating (1-5), text, date (ISO string) }
 *
 * No incluye insignias de "compra verificada": esa etiqueta solo debería
 * mostrarse cuando esté respaldada por un pedido real.
 */
window.VDT_REVIEWS = [
    { name: 'María G.', initials: 'MG', rating: 5, date: '2026-06-02',
      text: 'El vaso térmico mantiene el café caliente toda la mañana y el diseño es precioso.' },
    { name: 'Javier R.', initials: 'JR', rating: 5, date: '2026-05-18',
      text: 'Se nota la calidad artesanal en cada detalle. Ya pedí el pack de regalo para toda mi familia.' },
    { name: 'Sofía L.', initials: 'SL', rating: 5, date: '2026-06-21',
      text: 'La experiencia de compra se siente premium de principio a fin. Volvería a comprar sin dudarlo.' },
    { name: 'Diego F.', initials: 'DF', rating: 4, date: '2026-04-30',
      text: 'Muy contento con la compra, el producto llegó rápido y la calidad supera mis expectativas.' },
    { name: 'Lucía P.', initials: 'LP', rating: 5, date: '2026-05-05',
      text: 'Llevo varias semanas usando el matcha por las mañanas y la diferencia con lo que compraba antes es notable.' },
    { name: 'Martín A.', initials: 'MA', rating: 4, date: '2026-03-22',
      text: 'Buen producto en general. El envío tardó un par de días más de lo esperado pero valió la pena.' },
    { name: 'Carla N.', initials: 'CN', rating: 5, date: '2026-06-10',
      text: 'Regalé el set de iniciación y fue un éxito total. La presentación es muy cuidada.' },
    { name: 'Tomás V.', initials: 'TV', rating: 5, date: '2026-05-27',
      text: 'Compré el blend signature y es de lo mejor que probé en mucho tiempo. Aroma increíble.' }
];
