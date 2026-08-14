# Interkont — frontend Astro (WordPress headless)

Las 9 páginas del sitio, consumiendo contenido real desde WordPress vía
WPGraphQL. Mismo diseño y animaciones que el sitio estático original
(`../index.html`, `../cobra.html`, etc.) — el runtime `dc-runtime.js` no se
tocó, solo se generó el mismo documento con los títulos/párrafos "planos"
reemplazados por datos de WordPress.

| Ruta | Página | Origen WP |
|---|---|---|
| `/` | Home | page `home` |
| `/cobra` | COBRA | page `cobra` |
| `/panal` | PANAL | page `panal` |
| `/ik-labs` | IK Labs | page `ik-labs` |
| `/productos` | Nuestros productos | page `productos` |
| `/nosotros` | Nosotros | page `nosotros` |
| `/blog` | Blog | page `blog` |
| `/articulo` | Artículo | **post** `articulo` |
| `/catalogo-iad` | Catálogo IAD | page `catalogo-iad` |

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

## Cómo se generaron las páginas

Ninguna se escribió a mano: cada una se generó con un script que parte del
`.html` original correspondiente y reemplaza los bloques de texto "planos"
(títulos y párrafos sin ícono ni animación) por expresiones `{blocks[n]}`
que leen la respuesta de WPGraphQL, conservando la etiqueta y las clases
originales (`<h2 class="h2">{blocks[n]}</h2>`, nunca el texto suelto). El
orden coincide con el de creación en WordPress (ver
`../elementor/create_wp_pages.py`). El resto del documento —header,
tarjetas, tablero con parallax, marquesina, footer— queda exactamente
igual al original.

Nota de contenido: en `catalogo-iad`, el H1 en WordPress quedó como texto
plano ("Esta sección está en obra"), sin el `<br><em>` que le da el salto
de línea y la cursiva en el diseño original — se puede corregir editando
ese heading en WordPress si se quiere recuperar el efecto visual exacto.

## Pendiente

- Reemplazar los queries individuales por rutas dinámicas
  (`src/pages/[slug].astro`), ahora que las 9 páginas siguen el mismo patrón.
- ~~Conectar a Vercel + webhook de WordPress para rebuild automático al
  publicar contenido.~~ Hecho: `elementor/wp-vercel-deploy-hook.php` dispara
  Vercel (preview) y GitHub Pages (producción, interkont.co) al publicar.
- Revisar visualmente cada página contra su versión estática original.
