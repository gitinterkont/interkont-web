# Interkont — Importación en Elementor (WordPress)

Nueve plantillas JSON listas para importar, una por página.

---

## Contenido

| Archivo | Página |
|---|---|
| `01-home.json` | Home |
| `02-cobra.json` | COBRA |
| `03-panal.json` | PANAL |
| `04-ik-labs.json` | IK Labs |
| `05-productos.json` | Nuestros productos |
| `06-nosotros.json` | Nosotros |
| `07-blog.json` | Blog |
| `08-articulo.json` | Artículos del blog |
| `09-catalogo-iad.json` | Catálogo IAD |

Más la carpeta `assets/` con las 34 imágenes y el video.

---

## Pasos

### 1. Subir los assets

Suba el **contenido** de `assets/` por FTP a:

```
/wp-content/uploads/interkont/
```

Debe quedar así, respetando las subcarpetas:

```
/wp-content/uploads/interkont/LOOP.mp4
/wp-content/uploads/interkont/hero-poster.jpg
/wp-content/uploads/interkont/IMG FONDO-eba0b50c.png
/wp-content/uploads/interkont/logos/…
/wp-content/uploads/interkont/marcas/…
/wp-content/uploads/interkont/premios/…
```

> Por FTP, no por la biblioteca de medios: WordPress renombra los archivos y rompería las rutas.

### 2. Ajustar el dominio

Cada JSON apunta a `https://TU-SITIO.com/wp-content/uploads/interkont/`.

Antes de importar, abra cada archivo en un editor de texto y reemplace `TU-SITIO.com` por su dominio real.

### 3. Importar

En WordPress: **Plantillas → Plantillas guardadas → Importar plantillas** y suba los nueve archivos.

### 4. Publicar cada página

1. Cree la página (**Páginas → Añadir nueva**).
2. Edite con Elementor.
3. En **Ajustes de página → Diseño de página**, elija **Elementor Canvas**.
4. Desde la carpeta de plantillas, inserte la que corresponda.
5. Publique.

**Slugs esperados** (los enlaces internos ya apuntan ahí):

```
/            → Home
/cobra       → COBRA
/panal       → PANAL
/ik-labs     → IK Labs
/productos   → Nuestros productos
/nosotros    → Nosotros
/blog        → Blog
/articulo    → Artículos
/catalogo-iad → Catálogo IAD
```

---

## Cómo está construida cada plantilla

Una sección a ancho completo, con una columna y tres widgets HTML:

1. **Estilos** — fuente Mulish y toda la hoja de estilos.
2. **Marcado** — el sprite de iconos, header, contenido y footer.
3. **Script** — la lógica de la página, envuelta en un arranque autónomo.

Este enfoque conserva el diseño **exactamente** como está: parallax, cursor con luz, tablero animado, carrusel de marcas, slider de casos, pestañas y el conmutador de tema.

---

## Requisitos

- **Elementor** 3.0 o superior (funciona con la versión gratuita).
- El usuario que importa necesita permiso `unfiltered_html` — administrador en instalaciones de un solo sitio. En multisitio, actívelo con un plugin como *Unfiltered MU*.
- Plantilla **Elementor Canvas** en cada página: el diseño trae su propio header y footer, así que el del tema sobra.

---

## Consideraciones

**No son widgets nativos de Elementor.** El contenido vive en widgets HTML, así que se edita como código, no con los controles visuales de Elementor. Fue una decisión deliberada: convertir a widgets nativos habría descartado el tablero con scroll, el parallax, el cursor y las animaciones por timeline.

**Si prefiere edición visual**, el camino recomendado es convertir por partes: dejar las secciones tipográficas (títulos, párrafos, botones) como widgets nativos y mantener en HTML solo los bloques con lógica propia — tablero, sliders y carrusel. Puedo prepararlo así si le sirve.

**Un solo widget de script por página.** Lleva una guarda (`window.__ikBooted`) para no ejecutarse dos veces si se duplica la sección.

**El footer y el header se repiten en cada plantilla.** Si prefiere gestionarlos una sola vez, Elementor Pro permite moverlos al Theme Builder.
