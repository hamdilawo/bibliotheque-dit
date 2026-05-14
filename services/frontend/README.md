# react-app-starter
Application full-stack basée sur **TanStack Start** (Router + SSR) avec **Bun**, **Tailwind CSS**, **TanStack Query** et **i18n via Lingui**.

## Stack & dépendances (principales)
- **Runtime / Tooling**: Bun
- **Framework SSR**: `@tanstack/react-start`
- **Routing**: `@tanstack/react-router` (file-based)
- **Data fetching / cache**: `@tanstack/react-query` + devtools
- **i18n**: `@lingui/core`, `@lingui/react` + `lingui.config.js`
- **Styling**: Tailwind CSS v4 (`tailwindcss`, `@tailwindcss/vite`) + `tw-animate-css`
- **UI (shadcn/ui)**: composants dans `src/shared/components/ui/*` (config dans `components.json`)
- **UI utils**: `clsx`, `tailwind-merge`, `class-variance-authority`
- **Toasts**: `sonner`
- **Theme**: `next-themes`
- **HTTP client**: `ky`
- **Images**: `@unpic/react` (Composant `Image` pour des images optimisées)
- **State (optionnel)**: `jotai`

## Structure du projet
- `src/app/` : routes (file-based) — ex:
  - `src/app/__root.tsx`
  - `src/app/$lang/index.tsx`
  - `src/app/$lang/about.tsx`
- `src/middlewares/` : middlewares TanStack Start (ex: i18n)
- `src/shared/` : composants partagés, providers, stores
- `src/lib/` : utilitaires (ex: `cn`, i18n utils, http client)
- `src/locales/` : catalogues Lingui (`fr`, `en`)
- `server.ts` : serveur **Bun** de prod (sert `dist/client` + fallback vers `dist/server/server.js`)

## Prérequis
- Bun installé (version récente)

## Installation
```bash
bun install
```

## Développement
Lance Vite en dev :
```bash
bun --bun vite dev
```

Routes i18n (exemples) :
- `http://localhost:3000/fr`
- `http://localhost:3000/fr/about`
- `http://localhost:3000/en`
- `http://localhost:3000/en/about`

## Build (production)
Génère `dist/client` + `dist/server` :
```bash
bun --bun vite build
```

## Lancer en production (sans Docker)
1) Build :
```bash
bun --bun vite build
```

2) Démarrer le serveur :
```bash
bun run server.ts
```

Variables d’environnement utiles (voir `server.ts`) :
- `PORT` (default: 3000)
- `ASSET_PRELOAD_MAX_SIZE` (default: 5MB)
- `ASSET_PRELOAD_INCLUDE_PATTERNS`
- `ASSET_PRELOAD_EXCLUDE_PATTERNS`
- `ASSET_PRELOAD_VERBOSE_LOGGING`
- `ASSET_PRELOAD_ENABLE_ETAG`
- `ASSET_PRELOAD_ENABLE_GZIP`

## shadcn/ui
Ce projet utilise **shadcn/ui**.
- Configuration: `components.json`
- Composants générés: `src/shared/components/ui/`

### Ajouter un composant
Exemple (bouton) :
```bash
bunx shadcn@latest add button
```

## i18n (Lingui)
### Extraire les messages
```bash
bun run extract
```

### Compiler les catalogues
```bash
bun run compile
```

## Tests / Qualité
### Tests
Il n’y a pas forcément de tests au départ.
```bash
bun test
```

### Typecheck
```bash
bun x tsc -p tsconfig.json --noEmit
```

## Optimisation des Images
Ce projet utilise `@unpic/react` pour servir des images optimisées.

Exemple d'utilisation :
```tsx
import { Image } from '@unpic/react'

export function MyComponent() {
  return (
    <Image
      src="/logo192.png"
      layout="constrained"
      width={192}
      height={192}
      alt="Logo"
    />
  )
}
```

## Déploiement Docker (prod)
Le projet contient un `Dockerfile` multi-stage optimisé et un `.dockerignore`.

### Build de l’image
```bash
docker build -t my-tanstack-app:prod .
```

### Run
```bash
docker run --rm -p 3000:3000 -e PORT=3000 my-tanstack-app:prod
```