# Orbita

App social móvil centrada en **descubrir personas → hablar → conseguir respuesta →
conversar → (amistad, conocer gente o citas, si ambas partes quieren)**. Ver
`docs/01-product-spec.md` para la especificación completa del producto.

## Estructura del monorepo

```
apps/
  mobile/   App Expo (React Native + TypeScript) — iOS, Android y web
  admin/    Panel de administración (Next.js)
packages/
  shared/   Tipos y lógica de negocio pura compartida (economía, rachas, config)
supabase/
  migrations/  Esquema SQL versionado (Postgres + RLS)
  seed.sql     Valores por defecto de configuración e intereses
docs/       Especificación, arquitectura, base de datos, UX/UI, seguridad, roadmap
```

## Empezar

```bash
npm install                          # instala todo el monorepo (workspaces)
npm run test                         # tests de packages/shared
npm run mobile                       # arranca la app Expo (necesita apps/mobile/.env — ver .env.example)
npm run admin                        # arranca el panel admin (necesita apps/admin/.env.local — ver .env.example)
```

Ambas apps necesitan un proyecto Supabase real (gratuito) con las migraciones de
`supabase/migrations/` aplicadas — ver `docs/02-architecture.md` y
`docs/05-mvp-scope-and-testing.md` para cómo validarlas localmente sin necesidad de Docker.

## Documentación

Empieza por `docs/ASSUMPTIONS.md` (decisiones tomadas de forma autónoma) y
`docs/01-product-spec.md`. El resto de documentos numerados siguen las fases del proyecto:
arquitectura, base de datos, UX/UI, alcance del MVP y evidencia de pruebas, seguridad y
privacidad, y roadmap.

---

## Landing "Cyber-Minimalism" (legacy)

El archivo `index.html` en la raíz es una landing page independiente ("VDT"), construida
con Tailwind CSS, Three.js y GSAP, sin relación con el proyecto Orbita. Se abre
directamente en un navegador, sin build ni instalación.
