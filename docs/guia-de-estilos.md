# Manual de marca y guía de estilos
## Interkont — GovTech · Sitio web

---

## 1. Identidad

**Interkont** es el brazo tecnológico para la transparencia del sector público. Once años monitoreando la inversión del Estado, hoy con inteligencia artificial.

- **Tono:** técnico pero cercano. Afirmaciones concretas, cero jerga vacía.
- **Trato:** usted (institucional) en COBRA, Productos y Nosotros. Tú (más directo) en IK Labs, por su carácter AI-first.
- **Firma:** *Powerful Technology*.
- **Concepto interno:** "fábrica de ideas" y "Efecto Wow" — productos estéticos, funcionales y que entregan algo más.

### Nomenclatura correcta

| Sí | No |
|---|---|
| COBRA (plataforma insignia) | Cobra |
| IK Labs (unidad AI-first) | IKLabs / IK LABS |
| GESPRO = plataforma del Ministerio del Interior (**cliente**) | GESPRO como producto de Interkont |
| Catálogo IAD | catálogo iad |

> **Solo hay dos productos: COBRA e IK Labs.**

---

## 2. Color

### Paleta base

| Rol | Token | Hex |
|---|---|---|
| Magenta de marca | `--mag` | `#EA215E` |
| Magenta claro (sobre oscuro) | `--mag-lt` | `#FF5C86` |
| Tinte magenta (fondos suaves) | `--mag-tint` | `#FCE7EF` |
| Negro tinta | `--ink` | `#131117` |
| Gris texto secundario | `--ink-soft` | `#66646E` |
| Oscuro de contenedores | `--dark` | `#17151D` |
| Oscuro con imagen | — | `#0b0910` |
| Gris muy claro (superficie) | `--sheet` | `#F4F3F5` |
| Blanco | `--white` | `#FFFFFF` |
| Línea / borde | `--line` | `#E8E6EB` |

### Degradado de marca

```css
--grad:   linear-gradient(92deg,  #E70147 0%, #FFAA4A 100%);
--grad-r: linear-gradient(120deg, #E70147 0%, #FFAA4A 100%);
```

Es el acento principal del sitio. Se aplica en:

- Botones primarios (`.btn-mag`)
- Tiles de iconos, badges y avatares
- Texto de eyebrows y cifras destacadas (vía `background-clip: text`)
- Trazos de gráficas, gauges y barras activas
- Pestaña activa y subrayados de estado

**Nunca** en fondos de sección completos ni en párrafos de texto corrido.

### Fondo del sitio

```css
background: radial-gradient(80% 46% at 50% 30%, rgba(234,33,94,.08), transparent 62%), #EFEEF2;
```

---

## 3. Tipografía

**Familia única: Mulish** (Google Fonts, pesos 400–900).

| Uso | Tamaño | Peso | Tracking |
|---|---|---|---|
| H1 hero | `clamp(40px, 6vw, 80px)` | 800 | `-.04em` |
| H2 sección | `clamp(34px, 5vw, 60px)` | 800 | `-.035em` |
| H3 tarjeta grande | `clamp(24px, 3vw, 40px)` | 800 | `-.025em` |
| H4 tarjeta | 17–19px | 800 | `-.02em` |
| Párrafo destacado (`.big`) | `clamp(17px, 1.7vw, 23px)` | 500 | normal |
| Cuerpo | 14–16.5px | 400 | normal |
| Eyebrow | 13px | 700 | `.01em` |
| Etiqueta / línea | 12px | 800 | `.1em` + mayúsculas |
| Cifra grande | `clamp(42px, 6vw, 70px)` | 900 | `-.045em` |

Reglas: títulos siempre 800/900 con tracking negativo apretado. `line-height` de 0.98–1.05 en titulares, 1.6 en cuerpo. `text-wrap: pretty` en párrafos largos.

---

## 4. Layout y espaciado

### Contenedor

```css
.wrap { max-width: 1360px; margin: 0 auto; padding: 0 clamp(16px, 3vw, 40px); }
```

Estilo Nubank: contenido casi de borde a borde, márgenes anchos, mucho aire — nunca encajonado.

### Radios

| Token | Valor | Uso |
|---|---|---|
| `--r-xl` | 34px | Bandas y contenedores grandes |
| `--r-lg` | 26px | Tarjetas |
| `--r` | 18px | Elementos internos |
| — | 100px | Botones, chips, navbar |

### Sombras

```css
--sh:    0 2px 8px rgba(19,17,23,.04), 0 20px 44px -22px rgba(19,17,23,.16);
--sh-lg: 0 8px 20px rgba(19,17,23,.06), 0 40px 80px -30px rgba(19,17,23,.28);
```

### Ritmo vertical

- Sección: `padding: clamp(56px, 7vw, 100px) 0`
- Cierre (CTA final): `clamp(80px, 10vw, 130px)`
- Márgenes laterales de bandas: `clamp(16px, 2.6vw, 34px)`

### Regla de layout

Grupos de elementos hermanos siempre con `display: flex` / `grid` + `gap`. Nunca espaciados por márgenes individuales ni espacios en blanco del código.

---

## 5. Componentes

### Botones

| Variante | Fondo | Uso |
|---|---|---|
| `.btn-mag` | Degradado de marca | CTA principal |
| `.btn-dark` | `--ink` | CTA de navbar y secundario |
| `.btn-light` | Blanco + borde | Terciario sobre claro |
| `.btn-glass` | Vidrio translúcido | Sobre hero oscuro |

Todos: `border-radius: 100px`, `padding: 14px 26px`, peso 700, `translateY(-2px)` al hover, icono que se desplaza 3px.

### Navbar flotante

Píldora despegada del borde, ancho `calc(100% - 2*margen)`, radio 100px. El vidrio va en un `::before` (para que `backdrop-filter` no cree bloque contenedor).

- Sobre hero: `rgba(20,17,26,.42)` + blur, logo y enlaces blancos.
- Con scroll (`.scrolled`): `rgba(255,255,255,.82)` + blur, logo y enlaces oscuros.
- Móvil (≤960px): panel desplegable anclado bajo la píldora, controlado por `body.navopen`.

**Navegación oficial:** Interkont · Soluciones (desplegable: COBRA, IK Labs) · Nuestros productos · Blog · Catálogo IAD · **Contáctanos** (botón).

### Tarjetas

- **Clara:** blanco + `--sh`, hover `translateY(-6px)` + `--sh-lg`.
- **Oscura:** imagen de fondo con parallax, sin velo.
- **Vidrio:** `rgba(255,255,255,.07)` + `blur(14px)` + borde interior — para tarjetas dentro de bandas con imagen.

Cada tarjeta abre con un tile de icono de 46–52px, radio 12–14px, degradado de fondo e icono blanco.

### Hero

Pantalla completa (`100vh`), fondo oscuro con textura diagonal + glow radial de marca, rejilla enmascarada. En el landing, video en bucle silenciado con velo. Contenido alineado a la izquierda: eyebrow → H1 → subtítulo → dos botones.

### Pestañas

Rail lateral en desktop (`sticky`), scroll horizontal en móvil. Activa: fondo con imagen parallax, texto blanco, tile en degradado.

---

## 6. Imagen de fondo y parallax

Los contenedores oscuros usan la imagen de marca con:

```css
background-image: url("uploads/IMG FONDO-eba0b50c.png");
background-size: cover;
background-position: center;
background-attachment: fixed;
```

**Sin capa de opacidad negra** — la imagen se ve tal cual.

> **Regla crítica:** `background-attachment: fixed` es incompatible con `transform`. Los contenedores con parallax animan solo con `opacity` (`animation-name: rv-fade`) y no llevan hover con desplazamiento.

Aplicado en: footer, banda Catálogo IAD, Misión y visión, bandas de estadísticas, Eye Control, experiencia de usuario, tarjeta del CEO, modelos de licenciamiento y pestaña activa.

---

## 7. Iconografía

Estilo **Lucide**: trazo lineal, `stroke-width: 2`, `stroke-linecap` y `linejoin` redondeados, sin relleno.

Implementados como `<symbol>` en un sprite SVG al inicio de cada página, invocados con `<use href="#i-nombre">`. Tamaños: 15–24px según contexto.

**Sin emoji.** Sin ilustraciones dibujadas en SVG — para imágenes reales se usan placeholders.

---

## 8. Movimiento

### Aparición en scroll

CSS puro, sin JavaScript:

```css
.rv { opacity: 1; transform: none; }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    @keyframes rv-in { from { opacity:0; transform:translateY(28px) } to { opacity:1; transform:none } }
    .rv { animation: rv-in .8s cubic-bezier(.2,.7,.3,1) both;
          animation-timeline: view(); animation-range: entry 0% cover 22%; }
  }
}
```

El contenido es visible por defecto — ningún re-render puede ocultarlo.

### Cursor personalizado

Dos elementos que siguen al ratón (solo en `hover: hover` y `pointer: fine`):

- `#ikcur` — punto de 9px con degradado de marca, seguimiento inmediato.
- `#ikring` — anillo de trazo de 42px, seguimiento suavizado (`lerp 0.16`).

Estados: sobre elementos interactivos, cards y vectores el punto se reduce a 6px y el anillo crece a 86px aplicando `backdrop-filter: blur(6px)`. Al pulsar, el anillo se contrae a 32px.

Ambos arrancan invisibles y aparecen con el primer movimiento. Se desactivan con `prefers-reduced-motion`.

### Curvas y duraciones

- Entrada: `cubic-bezier(.2,.7,.3,1)`, 0.8s
- Hover: 0.2–0.35s
- Transiciones de estado: 0.22–0.4s

---

## 9. Arquitectura del sitio

| Archivo | Contenido |
|---|---|
| `Interkont Landing.dc.html` | Home: hero con video, ¿Qué es Interkont?, Misión y visión, tablero COBRA, productos, Catálogo IAD, CTA |
| `COBRA.dc.html` | Producto: hero, estadísticas, diagrama de actores, 6 funciones, Eye Control, experiencia de usuario |
| `IK Labs.dc.html` | Producto: hero, estadísticas, capacidades, AI Software Factory (12), IK Agent Suite (7), IK Data Agent, modelo comercial, inversión |
| `Productos.dc.html` | Catálogo en 9 pestañas: Cloud, Corporate, Housing, Niveles, Soporte, BPM, IA, Otros servicios, Política de usuarios |
| `Nosotros.dc.html` | Empresa: acerca de, equipo, datos, palabra del CEO |
| `Blog.dc.html` | Índice: destacado + 9 entradas filtrables por categoría |
| `Articulo.dc.html` | 10 artículos completos, enrutados por hash (`#slug`) |

**El header y el footer son globales e idénticos en todas las páginas.** Cualquier página nueva los hereda sin variación.

---

## 10. Reglas rápidas

1. Degradado de marca solo en acentos: botones, tiles, cifras, trazos. Nunca en fondos de sección ni texto corrido.
2. Máximo dos fondos: claro (`#EFEEF2`) y oscuro con imagen (`#0b0910`).
3. Títulos en 800/900 con tracking negativo. Siempre Mulish.
4. Esquinas muy redondeadas; botones y navbar en píldora.
5. Contenido de borde a borde con márgenes anchos — nunca encajonado.
6. Iconos de línea estilo Lucide. Sin emoji.
7. Contenedores con parallax: nunca `transform`.
8. Elementos hermanos con flex/grid + gap.
9. Sin relleno: si una sección se siente vacía es un problema de layout, no de contenido.
10. Todo lo que oculte contenido debe degradar a visible — el usuario nunca ve una página en blanco.
