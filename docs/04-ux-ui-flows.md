# UX/UI y navegación (FASE 4)

## 1. Identidad visual propia

Ni Tinder (rojo/blanco, cards de swipe) ni Wizz (amarillo neón, grid tipo "radar"). Identidad
propia de Orbita:

- **Paleta**: fondo oscuro por defecto (`#0B0B12` base, tarjetas `#15151F`), acento primario
  **"Coral Aurora"** `#FF5D73` (energía, cálido, distinto del rojo Tinder y del amarillo Wizz),
  acento secundario **"Violeta Nebula"** `#8B7CFF` para elementos premium/gamificación
  (monedas, super likes, racha), verde `#3DDC97` para estados positivos (en línea, leído,
  éxito), y modo claro completo como alternativa (no solo dark mode).
- **Tipografía**: `Sora` para títulos (geométrica, moderna, con personalidad) y `Inter` para
  texto/UI (máxima legibilidad en tamaños pequeños de chat).
- **Forma**: esquinas muy redondeadas (`radius` 20-28px) en cards y burbujas de chat,
  look "premium suave" en vez de esquinas afiladas.
- **Motion**: transiciones con `react-native-reanimated` (spring, no linear) — las cards de
  descubrimiento tienen una micro-animación de entrada, los logros/recompensas usan confetti
  ligero, el envío de Super Like tiene un pulso de color.
- Todo esto está centralizado en `apps/mobile/src/theme/` (tokens de color/tipografía/espaciado
  reutilizables) — ningún color hardcodeado por pantalla.

## 2. Navegación inferior

```
┌──────────┬──────────┬──────────┬──────────┐
│ Descubrir │ Mensajes │ Actividad │ Perfil   │
│   🧭      │   💬 (n) │   ⚡ (n)  │   👤     │
└──────────┴──────────┴──────────┴──────────┘
```

- **Descubrir**: feed principal de personas.
- **Mensajes**: conversaciones activas + banner destacado de "Te han hablado" (solicitudes
  pendientes) arriba del todo — máximo protagonismo tal como pide el brief, sin esconderlo en
  un tab aparte que nadie visita.
- **Actividad**: Quién te ha visto, Admiradores secretos, Super Likes recibidos, racha diaria,
  logros.
- **Perfil**: perfil propio, edición, monedas/tienda, ajustes, Premium.

Badges numéricos en Mensajes (solicitudes + no leídos) y Actividad (eventos nuevos) para
incentivar el regreso — gamificación de reenganche sin ser invasiva.

## 3. Flujo de onboarding (10 pasos del brief → 8 pantallas, agrupando lo rápido)

1. Crear cuenta (email + password; UI preparada para añadir Google/Apple después).
2. Nombre + fecha de nacimiento (un solo step, valida 18+ al vuelo).
3. Género (con opción "prefiero no decirlo") + a quién quiere conocer.
4. Qué busca (chips multi-selección: Amistad / Conocer gente / Citas — no excluyentes).
5. Ciudad (autocompletado simple; permiso de ubicación opcional para "cerca de ti").
6. Foto principal (obligatoria, con recorte) — paso con mayor abandono típico, por eso va
   solo con 1 foto obligatoria y el resto se anima a subir después desde el perfil.
7. Bio + intereses (chips preexistentes + libres).
8. Resumen + preferencias de descubrimiento (rango de edad, distancia) → barra de "perfil
   completado al X%" con CTA a completar el resto más tarde (no bloquea la entrada al feed).

Cada paso guarda progreso (`profiles` se va rellenando incrementalmente), así que cerrar la
app a mitad de onboarding no pierde el avance.

## 4. Pantalla Descubrir

- Card apilada (una persona a la vez, con indicador de más al fondo) — **no es swipe binario
  like/no-like**: el gesto principal es *tap* para expandir bio/fotos/intereses, y las
  acciones son botones explícitos:
  - `Hablar` (abre un composer inline para el primer mensaje, no un simple "like" silencioso).
  - `Super Like` (icono violeta, feedback inmediato).
  - `Pasar` (siguiente persona, gesto swipe lateral opcional además del botón, para quien
    venga de apps tipo Tinder y busque ese gesto por costumbre).
- Estado vacío: "No hay más personas por ahora cerca de ti" + sugerencia de ampliar el rango
  de distancia/edad en preferencias (nunca una pantalla en blanco sin explicación).

## 5. Perfil (propio y ajeno)

- Header con foto principal a pantalla completa, nombre + edad + ciudad superpuestos con
  gradiente (legibilidad sin perder la foto).
- Galería: grid de fotos públicas + celda final `+N 🔒` con blur/candado si hay fotos
  bloqueadas — al tocar, modal explicando *cómo* desbloquear (monedas o Premium), nunca un
  muro sorpresa.
- Bio, intereses (chips), "Admiradores: N" si aplica, botones grandes `Hablar` / `Super Like`
  fijos al fondo (siempre accesibles sin scroll).
- Perfil propio añade: editar, ver estadísticas (vistas, admiradores, % completado),
  acceso a monedas/Premium.

## 6. "Te han hablado" (solicitudes)

Lista con foto + nombre + primer mensaje en preview + `Responder` / `Ignorar`. Responder abre
directamente el chat con el teclado ya activo (fricción mínima para cerrar el bucle
"conseguir que te respondan").

## 7. Chat

Burbujas redondeadas, ticks de enviado/recibido/leído, indicador "escribiendo..." con
animación de puntos, barra de adjuntar foto/emoji, menú superior con Bloquear/Reportar/
Silenciar/Eliminar. Mensajes de sistema (p. ej. "Has aceptado hablar con X") centrados y sutiles.

## 8. Estados vacíos, carga y error

Todos definidos como componentes reutilizables (`EmptyState`, `LoadingSkeleton`, `ErrorState`)
en `apps/mobile/src/components/` — nunca una pantalla en blanco o un spinner infinito sin
mensaje ni acción de reintento.

## 9. Accesibilidad y responsive

Tamaños táctiles mínimos 44x44pt, contraste AA en texto sobre imagen (gradiente calculado, no
fijo), soporte de tipografía dinámica del sistema, layout probado en anchos pequeños (iPhone
SE / gama baja Android) y grandes (tablets vía `apps/mobile` con breakpoints básicos).
