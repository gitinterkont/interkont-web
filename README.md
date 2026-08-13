# Interkont — Sitio GovTech

Sitio estático de nueve páginas, listo para publicar en GitHub Pages. Sin build, sin
dependencias externas en tiempo de ejecución: todo (React, la fuente Mulish, imágenes y
video) se sirve desde este mismo repositorio.

## Páginas

| URL | Archivo | Contenido |
|---|---|---|
| `/` | `index.html` | Home |
| `/cobra.html` | `cobra.html` | COBRA |
| `/panal.html` | `panal.html` | PANAL |
| `/ik-labs.html` | `ik-labs.html` | IK Labs |
| `/productos.html` | `productos.html` | Nuestros productos |
| `/nosotros.html` | `nosotros.html` | Nosotros |
| `/blog.html` | `blog.html` | Blog |
| `/articulo.html` | `articulo.html` | Artículos |
| `/catalogo-iad.html` | `catalogo-iad.html` | Catálogo IAD |

## Publicar en GitHub Pages

```bash
gh repo create interkont-govtech --public --source=. --remote=origin --push
```

Luego, en **Settings → Pages → Build and deployment → Source**, elija **GitHub Actions**.
El workflow `.github/workflows/deploy.yml` publica en cada push a `main`.

Alternativa sin Actions: en esa misma pantalla elija **Deploy from a branch** →
`main` / `/ (root)`. El archivo `.nojekyll` ya evita que Jekyll procese el sitio.

El sitio queda en `https://<usuario>.github.io/<repo>/`. Todos los enlaces son
relativos, así que funciona igual en la raíz de un dominio propio.

### Dominio propio

1. Cree el archivo `CNAME` en la raíz con el dominio (por ejemplo `www.interkont.co`).
2. Apunte el DNS a GitHub Pages.
3. Regenere `sitemap.xml`, `robots.txt` y las etiquetas `canonical`/`og:` con la URL
   real (ver *Regenerar* más abajo).

## Ver el sitio en local

```bash
python3 -m http.server 8000
```

Abra <http://localhost:8000>. Hace falta un servidor HTTP: abrir los `.html` con
`file://` no funciona porque el runtime carga scripts por ruta relativa.

## Estructura

```
index.html …            Nueve páginas + 404.html
assets/                 Imágenes, video y fuentes usadas por el sitio
  fonts/                Mulish auto-hospedada (woff2, subconjuntos latin)
vendor/                 dc-runtime.js, react + react-dom (UMD 18.3.1)
elementor/              Plantillas JSON para importar en WordPress (no se publica)
docs/                   Guía de estilos de marca
favicon.svg             Isotipo Interkont
sitemap.xml robots.txt  SEO
.nojekyll               Desactiva Jekyll en GitHub Pages
```

## Cómo funciona una página

Cada `.html` es autocontenido y tiene tres bloques:

1. **`<helmet>`** — la hoja de estilos completa de la página.
2. **Marcado** — sprite de iconos SVG, header, contenido y footer.
3. **`<script type="text/x-dc">`** — la lógica (`class Component extends DCLogic`):
   parallax, cursor con luz, carruseles, pestañas y conmutador de tema.

`vendor/dc-runtime.js` monta ese marcado con React. Los objetos `window.__resources`
declarados en el `<head>` de cada página redirigen React y ReactDOM a `vendor/`, de modo
que **no se hace ninguna petición a servidores externos** — importante en redes de
entidades públicas que bloquean CDNs.

Para editar contenido, modifique el marcado directamente en el `.html` correspondiente.
Los estilos están en el `<style>` dentro de `<helmet>`, en la misma página.

## Regenerar desde el export original

El sitio se generó con un script a partir del export `.dc.html`. Si vuelve a generarlo,
puede fijar la URL definitiva para que `canonical`, `og:` y `sitemap.xml` salgan
absolutos:

```bash
BASE_URL=https://www.interkont.co/ python3 tools/build.py
```

Sin `BASE_URL` las URLs quedan relativas, que es lo que hay ahora.

## Notas

- El sitio se renderiza en el cliente: sin JavaScript no se ve contenido. Google lo
  indexa, pero si el SEO es crítico conviene pre-renderizar el HTML.
- `elementor/` guarda las plantillas para WordPress y no forma parte del sitio
  publicado. Los assets que pide `elementor/LEEME.md` son los de `assets/`.
- La fuente Mulish se distribuye bajo SIL Open Font License 1.1.
