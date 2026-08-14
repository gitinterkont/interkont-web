# Interkont — Sitio GovTech

Sitio de Interkont migrado de HTML estático a una arquitectura **headless**:
WordPress como backend de contenido, [Astro](https://astro.build) como frontend,
desplegado en [Vercel](https://vercel.com).

## Stack

| Capa | Herramienta | Rol |
|---|---|---|
| Contenido | WordPress (`cms.interkont.co`) | Backend headless — sin tema, sin Elementor. Se edita ahí (títulos, párrafos, artículos del blog) |
| API de contenido | [WPGraphQL](https://www.wpgraphql.com/) + [WPGraphQL Content Blocks](https://github.com/wpengine/wp-graphql-content-blocks) | Expone las páginas/posts de WordPress como bloques de Gutenberg vía GraphQL |
| Frontend | [Astro](https://astro.build) (`astro-site/`) | Genera el sitio estático consumiendo WPGraphQL en build time. Mismo diseño, tipografía y animaciones que el sitio original |
| Hosting | [Vercel](https://vercel.com) | Build y despliegue del frontend |

## Páginas

| Ruta | Origen en WordPress |
|---|---|
| `/` | page `home` |
| `/cobra` | page `cobra` |
| `/panal` | page `panal` |
| `/ik-labs` | page `ik-labs` |
| `/productos` | page `productos` |
| `/nosotros` | page `nosotros` |
| `/blog` | listado dinámico de posts (destacado, filtros por categoría y tarjetas) |
| `/articulo/[slug]` | **posts** de WordPress, uno por artículo — ruta dinámica, no una página por artículo |
| `/catalogo-iad` | page `catalogo-iad` (hero) + visor/simulador de catálogo que consume un endpoint de Google Apps Script (pendiente migrar a un CPT de WordPress) |

## Desarrollo local

```bash
cd astro-site
npm install
npm run dev
```

Por defecto apunta a `https://cms.interkont.co/graphql`. Para usar otro backend,
copie `.env.example` a `.env` y ajuste `WP_GRAPHQL_ENDPOINT`.

## Cómo se generaron las páginas de Astro

Cada `.astro` en `astro-site/src/pages/` se generó a partir de su equivalente
`.html` original en la raíz del repo: se conservó el documento completo (estilos,
runtime de animaciones `dc-runtime.js`, marcado) y solo los títulos/párrafos
"planos" (sin ícono ni animación) se volvieron dinámicos, leyendo el contenido
real desde WordPress. El resto —header, tarjetas, tablero con parallax,
marquesina, footer— quedó intacto.

Los scripts en `elementor/` (`create_wp_pages.py`, `create_wp_articles.py`,
`assign_wp_categories.py`, `set_wp_excerpts.py`) fueron los que cargaron ese
contenido inicial en WordPress vía su API REST — se dejan en el repo como
referencia de cómo se sembró el contenido, no se vuelven a correr en el día a día.

## Estructura

```
astro-site/              Frontend Astro — el sitio que realmente se despliega
  src/pages/              Una página por ruta (o ruta dinámica, para artículos)
  public/assets/          Imágenes, video y fuentes (auto-hospedadas, sin CDN)
  public/vendor/          dc-runtime.js, react + react-dom (UMD 18.3.1)
elementor/                Scripts de migración de contenido hacia WordPress
docs/                     Guía de estilos de marca
index.html, cobra.html …  Sitio estático ORIGINAL — se conserva como referencia
                          de diseño durante la migración, ya no es lo que se publica
```

## Nota sobre los `.html` de la raíz

Los nueve archivos `.html` de la raíz (`index.html`, `cobra.html`, etc.) son el
sitio estático **original**, previo a esta migración. Se mantienen en el repo
como referencia de diseño — cada página de Astro se construyó a partir de su
`.html` correspondiente — pero **no son el sitio que está en producción**. El
sitio real vive en `astro-site/`.

## Licencias

La fuente Mulish se distribuye bajo SIL Open Font License 1.1.
