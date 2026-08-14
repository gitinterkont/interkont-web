# Interkont — frontend Astro (WordPress headless)

Piloto de la página Home consumiendo contenido real desde WordPress vía
WPGraphQL. Mismo diseño y animaciones que el sitio estático original
(`../index.html`) — el runtime `dc-runtime.js` no se tocó, solo se generó
el mismo documento con los títulos/párrafos "planos" reemplazados por datos
de WordPress.

## Desarrollo local

```bash
npm install
cp .env.example .env   # ajusta WP_GRAPHQL_ENDPOINT si hace falta
npm run dev
```

## Build de producción

```bash
npm run build
npm run preview
```

## Cómo se generó `src/pages/index.astro`

No se escribió a mano: se generó con un script que parte del `index.html`
original y reemplaza los 18 bloques de texto "planos" (títulos y párrafos
sin ícono ni animación) por expresiones `{blocks[n]}` que leen la
respuesta de WPGraphQL, en el mismo orden en que esos bloques se crearon
en WordPress (ver `../elementor/create_wp_pages.py`). El resto del
documento —header, tarjetas, tablero con parallax, marquesina, footer—
queda exactamente igual al original.

## Pendiente

- Portar las otras 8 páginas con el mismo patrón.
- Reemplazar el query hardcodeado de `id: "home"` por rutas dinámicas
  (`src/pages/[slug].astro`) una vez estén todas.
- Conectar a Vercel + webhook de WordPress para rebuild automático al
  publicar contenido.
