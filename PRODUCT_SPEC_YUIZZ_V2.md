# 📋 ESPECIFICACIÓN DE PRODUCTO: YUIZZ V2.0

**Versión:** 2.0  
**Estado:** 🔴 ESPECIFICACIÓN EN DESARROLLO  
**Fecha:** 28 Septiembre 2026  
**Pivote:** Pure-inspired, YUIZZ-native

---

## 🎯 VISIÓN

YUIZZ es una aplicación de citas para adultos elegante, minimalista y poderosa.

**Diferenciación vs Pure:**
- 3 fotos por perfil (vs 5-10)
- Sistema de hashtags funcional para discovery
- Algoritmo de compatibilidad avanzado
- Filtros premium poderosos
- Búsqueda por países
- 10% más económica
- Identidad visual propia (dark, sexy, elegante)

---

## 📱 CORE EXPERIENCE (FLUJO PRINCIPAL)

### Sesión típica del usuario

```
LOGIN → FEED PRINCIPAL → EXPLORAR → MATCH → CHAT

1. AUTENTICACIÓN (1 min)
   - Email/teléfono + contraseña
   - Verificación OTP
   - Seleccionar fotos
   - Rellenar hashtags
   - Listo

2. FEED PRINCIPAL (continuada)
   - Abrir app
   - Ver perfil (foto grande, nombre, edad, distancia, hashtags)
   - Botones: Like / Pass / SuperLike
   - Siguiente perfil
   - Máxima velocidad, máxima claridad

3. VER PERFIL COMPLETO (expandible)
   - 3 fotos (grande + thumbnail)
   - Nombre, edad, ubicación
   - Descripción
   - Hashtags
   - Qué busca
   - Tipo (individual/pareja)
   - Último visto
   - Botones: Like / Pass / SuperLike / Report / Block

4. MATCHES
   - Lista de matches
   - Foto pequeña
   - Nombre
   - "Enviar mensaje" directo
   - Ordenar por reciente

5. CHAT
   - Mensajes con timestamp
   - Soporte: texto, emojis, GIFs, fotos
   - Escribiendo...
   - Leído / No leído
   - Opciones: Bloquear, Reportar, Limpiar chat
```

---

## 🏗️ ESTRUCTURA DE DATOS

### PERFILES

#### Individual Profile
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "individual",
  "name": "Laura",
  "age": 27,
  "gender": "female",
  "city": "Madrid",
  "latitude": 40.4168,
  "longitude": -3.7038,
  "description": "Buscando citas y conocer gente",
  "hashtags": ["#Citas", "#Besos", "#Sexting", "#SinCompromiso"],
  "verified_age": true,
  "verified_photo": true,
  "active_at": "2026-09-28T14:30:00Z",
  "photos": [
    { "position": 1, "url": "photo1.jpg", "type": "main" },
    { "position": 2, "url": "photo2.jpg", "type": "secondary" },
    { "position": 3, "url": "photo3.jpg", "type": "sexy" }
  ]
}
```

#### Couple Profile
```json
{
  "id": "uuid",
  "type": "couple",
  "names": "Laura & Jorge",
  "primary_user": "user1_uuid",
  "secondary_user": "user2_uuid",
  "age_range": "27-29",
  "gender": "mixed",
  "city": "Madrid",
  "latitude": 40.4168,
  "longitude": -3.7038,
  "description": "Pareja abierta buscando tercero",
  "hashtags": ["#Parejas", "#Sexting", "#Juegos"],
  "photos": [
    { "position": 1, "url": "couple.jpg", "type": "main" },
    { "position": 2, "url": "couple2.jpg", "type": "secondary" },
    { "position": 3, "url": "couple3.jpg", "type": "sexy" }
  ]
}
```

### PREFERENCIAS DE USUARIO

```json
{
  "user_id": "uuid",
  "age_range": [18, 35],
  "gender_preference": ["female", "couple"],
  "distance_km": 25,
  "country": "Spain",
  "hashtag_filters": ["#Citas", "#Besos", "#SinCompromiso"],
  "show_couples": true,
  "show_verified_only": false,
  "premium_until": "2026-10-28",
  "created_at": "2026-09-28T14:30:00Z"
}
```

### INTERACCIONES

```json
{
  "id": "uuid",
  "actor_id": "uuid",
  "target_id": "uuid",
  "action": "like|pass|superlike",
  "match_found": false,
  "created_at": "2026-09-28T14:30:00Z"
}
```

### MATCHES

```json
{
  "id": "uuid",
  "user1_id": "uuid",
  "user2_id": "uuid",
  "status": "active|blocked|expired",
  "matched_at": "2026-09-28T14:30:00Z",
  "last_message_at": "2026-09-28T15:00:00Z",
  "unread_count_user1": 0,
  "unread_count_user2": 2
}
```

### MENSAJES

```json
{
  "id": "uuid",
  "match_id": "uuid",
  "sender_id": "uuid",
  "receiver_id": "uuid",
  "content": "Hola! ¿Qué tal?",
  "media_url": null,
  "is_read": true,
  "created_at": "2026-09-28T15:00:00Z"
}
```

---

## 🎨 SISTEMA DE HASHTAGS

### Categorías (completo)

**ACCIÓN FÍSICA** (12)
```
#Besos #Morder #Arañar #Masaje #Juegos #Caricias
#Sexting #Lencería #Privado #Noche #Público #Exploración
```

**TIPO DE RELACIÓN** (8)
```
#Citas #SinCompromiso #RelaciónAbierta #Parejas
#Solteros #Amistad #Conexión #Química
```

**INTENSIDAD** (6)
```
#Dominación #Sumisión #Roleplay #Fantasías #Suave #Intenso
```

**PERFIL ESPECÍFICO** (4)
```
#Individual #Pareja #Buscando #Experimental
```

**MOTIVACIÓN** (5)
```
#Encuentros #Conocer #Flirtear #Diversión #Serio
```

**Total:** ~35 hashtags curados
**Usuario selecciona:** 3-6 hashtags típicamente

---

## 🧮 ALGORITMO DE DESCUBRIMIENTO

### Cálculo de puntuación

```
SCORE = (H * 0.40) + (A * 0.20) + (D * 0.20) + (G * 0.10) + (V * 0.10)

Donde:
H = Hashtag Match (0-100)
A = Age Match (0-100)
D = Distance Match (0-100)
G = Gender Match (0-100)
V = Freshness/Activity (0-100)
```

### Ejemplo real

```
Usuario A busca:
- Edad: 25-35
- Género: Mujeres
- Distancia: ≤25km
- Hashtags: #Citas, #Besos, #SinCompromiso
- País: España

Usuario B (perfil):
- Edad: 28 → Score A = 100 (dentro de rango)
- Género: Mujer → Score G = 100 (coincide)
- Distancia: 12km → Score D = 95 (muy cercano)
- Hashtags: #Citas, #Besos, #Juegos → Score H = 66 (2/3 coinciden)
- Actividad: Última sesión hace 2h → Score V = 90 (activo)
- País: España ✓

SCORE FINAL = (66 * 0.40) + (100 * 0.20) + (95 * 0.20) + (100 * 0.10) + (90 * 0.10)
            = 26.4 + 20 + 19 + 10 + 9 = 84.4 puntos

→ Usuario B aparecerá en posición alta en feed de A
```

### Distribución de perfiles

```
60% - Compatibilidad alta (Score > 75)
30% - Compatibilidad media (Score 50-75)
10% - Exploración aleatoria (Score < 50)
      (Para evitar que la app se sienta limitada)
```

---

## 💎 SISTEMA DE PREMIUM

### Modelo de precios

**GRATIS**
- 50 likes/día
- 0 SuperLikes/día
- Filtros básicos (edad, distancia)
- Hashtags limitados visibles
- Sin filtro de país
- Perfil sin destacar
- $0

**PREMIUM - €7.99/mes** ⭐
- Likes ilimitados
- 5 SuperLikes/día
- Filtros avanzados (edad exacta, distancia 5/10/25/50/100km, país)
- Ver hashtags completos
- Ver quién te vio
- Perfil destacado
- Búsqueda por país
- Mensajes sin límite
- Boost incluido 1x/mes
- €7.99 / mes

**PREMIUM - €19.99/trimestre** 🎁 (20% descuento)
- Todo lo de Premium
- 3 Boosts incluidos
- €6.66/mes equivalente

**PREMIUM - €59.99/año** 🏆 (38% descuento)
- Todo lo de Premium
- 12 Boosts incluidos
- €5/mes equivalente

**BOOSTS - €4.99/unidad**
- Aparecer primero en 30min
- +300% visibilidad
- Acumulable
- Mostrar al inicio de sesión

### Comparativa

| Feature | Free | Premium |
|---------|------|---------|
| Likes/día | 50 | ∞ |
| SuperLikes/día | 0 | 5 |
| Filtros avanzados | No | Sí |
| Ver quién te vio | No | Sí |
| Búsqueda país | No | Sí |
| Destaque | No | Sí |
| Mensajes | Limitados | ∞ |
| Boosts | No | 1/mes |
| Precio | $0 | €7.99/mes |

---

## 🔐 SEGURIDAD Y MODERACIÓN

### VERIFICACIÓN DE EDAD

```
Requerido: Verificación en 3 niveles
1. Documento de identidad (en registro)
2. Selfie con documento (en registro)
3. Verificación de teléfono (en registro)
4. Validación manual (equipo)

NO se permite:
- Menores de 18 años
- Documentos falsos/expirados
- Foto de perfil no coincide con selfie
```

### MODERACIÓN DE FOTOS

```
AI Detection:
✗ Desnudos completos (100% precisión)
✗ Genitales visibles (99% precisión)
✗ Penetración/sexo explícito (99% precisión)
✗ Contenido CSAM (100% precisión)

Permitido con reglas:
✓ Lencería, bikini, ropa ajustada
✓ Sugerente pero sin desnudez
✓ Artístico/sensual

Si falla moderación:
→ Bloquear foto
→ Solicitar otra
→ Revisar manual si duda
→ Ban si infracciones repetidas
```

### PROTECCIÓN DE USUARIO

```
Reportar:
- Usuario spam/fake
- Contenido inapropiado
- Acoso/abuso
- Comercial/prostitución

Bloquear:
- Privado
- Inmediato
- No puede ver tu perfil
- No recibe mensajes

Otras medidas:
- Anti-spam automático
- Detección de bots
- Antiacoso
- GDPR/LOPDGDD compliant
```

---

## 🌍 SOPORTE INTERNACIONAL

### Fase 1: Países principales
```
España, Portugal, Francia, Italia, Alemania, 
Reino Unido, Países Bajos, Bélgica, Austria, Suiza
```

### Fase 2: Expansión
```
Latinoamérica, otras regiones europeas
```

### Características multipaís
```
- Buscar por país sin distancia
- Perfiles sin ubicación exacta (solo país)
- Timezone automático
- Idioma del usuario
- Regulaciones locales
```

---

## 📊 MÉTRICAS DE ÉXITO

```
Objetivo Mes 1:
- 5K usuarios registrados
- 30% verificación
- 2K fotos de perfil moderadas
- 100 matches

Objetivo Mes 3:
- 50K usuarios
- 50% verificación
- 20K chats activos
- 2K matches diarios
```

---

## 🚀 ROADMAP IMPLEMENTACIÓN

### FASE A: Base de Datos + API (2 días)
```
- Schema v2.0 con hashtags
- Endpoints discovery v2
- Algoritmo compatibilidad
- Moderación fotos AI
```

### FASE B: Frontend (3 días)
```
- UI/UX Dark mode
- Feed principal
- Perfil individual/pareja
- Hashtag selection
- Premium purchase
```

### FASE C: Seguridad (2 días)
```
- Verificación de edad
- AI moderation
- Sistema de reportes
- Bloqueos
```

### FASE D: Monetización (1 día)
```
- Stripe integration
- Premium features
- Boosts
- Analítica
```

**Total: ~8 días de desarrollo**

---

## 💡 PRINCIPIOS DE DISEÑO

```
1. MINIMALISMO
   - 3 fotos, no 10
   - Información esencial solo
   - Interfaz limpia

2. RAPIDEZ
   - Swipe fluido
   - Sin cargas largas
   - Decisiones rápidas

3. ELEGANCIA
   - Dark mode obligatorio
   - Espacios amplios
   - Tipografía premium

4. CONFIANZA
   - Verificación fuerte
   - Moderación visible
   - Privacidad clara

5. ADULTO
   - Tono atrevido pero sofisticado
   - No pornográfico
   - Sexy pero profesional
```

---

**Próximo: Empezar implementación de Schema v2.0 y API**
