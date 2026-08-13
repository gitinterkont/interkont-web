#!/usr/bin/env python3
"""Convierte el export .dc.html de Interkont en un sitio estatico desplegable en GitHub Pages."""
import os, re, shutil, subprocess, sys, urllib.parse
from pathlib import Path

SRC = Path("/home/deozelot/Downloads/Landing page Interkont GovTech")
OUT = Path("/home/deozelot/Downloads/interkont-govtech-pages")

PAGES = [
    # (archivo origen, slug destino, title, description)
    ("Interkont Landing.dc.html", "index.html",
     "Interkont — Claridad total sobre cada peso público",
     "Software GovTech para el control de la inversión pública: supervisión de obras y contratos, trazabilidad y datos para decidir mejor."),
    ("COBRA.dc.html", "cobra.html",
     "COBRA — Control de obras y contratos | Interkont",
     "COBRA centraliza la supervisión de obras y contratos públicos: avance, presupuesto, evidencia en campo y alertas en un solo lugar."),
    ("PANAL.dc.html", "panal.html",
     "PANAL — Simplificamos la manera de ayudar | Interkont",
     "PANAL organiza la ayuda social: focalización, entrega y seguimiento de beneficiarios con trazabilidad de punta a punta."),
    ("IK Labs.dc.html", "ik-labs.html",
     "IK Labs — Software, agentes y datos | Interkont",
     "IK Labs construye software a la medida, agentes de IA y productos de datos para operar mejor lo público."),
    ("Productos.dc.html", "productos.html",
     "Nuestros productos — La familia COBRA | Interkont",
     "Toda la familia de productos Interkont en un solo lugar: COBRA, PANAL, IK Labs y el catálogo IAD."),
    ("Nosotros.dc.html", "nosotros.html",
     "Nosotros — Tecnología enfocada en la transparencia | Interkont",
     "Somos amantes de la tecnología enfocada en la transparencia. Más de once años apoyando el control de lo público."),
    ("Blog.dc.html", "blog.html",
     "Blog — Ideas sobre lo público, la tecnología y los datos | Interkont",
     "Artículos de Interkont sobre gestión pública, tecnología, datos y transparencia."),
    ("Articulo.dc.html", "articulo.html",
     "Artículos | Interkont",
     "Artículos de Interkont sobre gestión pública, tecnología, datos y transparencia."),
    ("Catalogo IAD.dc.html", "catalogo-iad.html",
     "Catálogo IAD | Interkont",
     "Catálogo IAD de Interkont: soluciones disponibles para entidades públicas."),
]

LINK_MAP = {src: dst for src, dst, _, _ in PAGES}

# uploads/<origen> -> assets/<destino> (nombres sin espacios ni mayusculas)
ASSET_RENAMES = {
    "fondo 2-611aff76.png": "fondo-2-611aff76.png",
    "fondo 2.png": "fondo-2.png",
    "IMG FONDO-eba0b50c.png": "img-fondo-eba0b50c.png",
    "Rectangle 943.png": "rectangle-943.png",
    "Slide 16_9 - 3.png": "slide-16-9-3.png",
    "LOOP.mp4": "loop.mp4",
}

REACT_MAP = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js": "vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js": "vendor/react-dom.production.min.js",
}

FONT_CSS_URL = ("https://fonts.googleapis.com/css2?"
                "family=Mulish:wght@400;500;600;700;800;900&display=swap")
FONT_SUBSETS = {"latin", "latin-ext"}


def log(msg):
    print(f"  {msg}")


# ---------------------------------------------------------------- assets ----
def referenced_assets():
    """Todas las rutas uploads/... citadas en los HTML (markup, CSS y JS)."""
    found = set()
    for src, _, _, _ in PAGES:
        text = (SRC / src).read_text(encoding="utf8")
        for m in re.findall(r"uploads/[^\"'()\s\\]+", text):
            found.add(urllib.parse.unquote(m.split("#")[0].split("?")[0]))
    return sorted(found)


def copy_assets():
    OUT_ASSETS = OUT / "assets"
    missing = []
    for rel in referenced_assets():
        src_file = SRC / rel
        if not src_file.is_file():
            missing.append(rel)
            continue
        parts = Path(rel).parts[1:]  # quita "uploads/"
        name = ASSET_RENAMES.get(parts[-1], parts[-1])
        dst = OUT_ASSETS.joinpath(*parts[:-1], name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst)
    if missing:
        sys.exit(f"ERROR: assets citados pero inexistentes: {missing}")
    n = sum(1 for _ in OUT_ASSETS.rglob("*") if _.is_file())
    log(f"assets copiados: {n}")


# ----------------------------------------------------------------- fuentes ---
def vendor_fonts():
    """Descarga Mulish (subconjuntos latin) y escribe assets/fonts/mulish.css."""
    ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
    css = subprocess.run(["curl", "-sSfL", "--max-time", "30", "-A", ua, FONT_CSS_URL],
                         capture_output=True, text=True, check=True).stdout

    fonts_dir = OUT / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    kept = []
    for subset, block in blocks:
        if subset not in FONT_SUBSETS:
            continue
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        fname = f"mulish-{subset}-{weight}.woff2"
        subprocess.run(["curl", "-sSfL", "--max-time", "30", "-A", ua, url,
                        "-o", str(fonts_dir / fname)], check=True)
        kept.append(block.replace(url, fname))
    if len(kept) != len(FONT_SUBSETS) * 6:
        sys.exit(f"ERROR: se esperaban {len(FONT_SUBSETS)*6} @font-face, hay {len(kept)}")
    header = ("/* Mulish — Google Fonts (SIL Open Font License 1.1), auto-hospedada.\n"
              "   Subconjuntos latin y latin-ext. */\n")
    (fonts_dir / "mulish.css").write_text(header + "\n".join(kept) + "\n", encoding="utf8")
    log(f"fuentes auto-hospedadas: {len(kept)} archivos woff2")


# ---------------------------------------------------------------- favicon ----
def build_favicon():
    """Extrae el isotipo (los 4 paths magenta del logo) del sprite."""
    src = (SRC / "Interkont Landing.dc.html").read_text(encoding="utf8")
    symbol = re.search(r'<symbol id="ik-color".*?</symbol>', src, re.S).group(0)
    paths = [p for p in re.findall(r"<path\b[^>]*>", symbol) if 'fill="var(--mag)"' in p]
    if len(paths) != 4:
        sys.exit(f"ERROR: se esperaban 4 paths del isotipo, hay {len(paths)}")
    body = "\n  ".join(p.replace('fill="var(--mag)"', 'fill="#EA215E"') for p in paths)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="24 -6 124 194">\n  '
           + body + "\n</svg>\n")
    (OUT / "favicon.svg").write_text(svg, encoding="utf8")
    log("favicon.svg generado desde el isotipo de marca")


# ------------------------------------------------------------------ paginas --
HEAD_EXTRA = """<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#EA215E">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="Interkont">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/mulish-latin-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/mulish-latin-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts/mulish.css">
<script>window.__resources={resources};</script>"""

RESOURCES_JSON = (
    '{"https://unpkg.com/react@18.3.1/umd/react.production.min.js":'
    '"vendor/react.production.min.js",'
    '"https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js":'
    '"vendor/react-dom.production.min.js"}'
)


def transform_page(src_name, dst_name, title, desc, base_url):
    text = (SRC / src_name).read_text(encoding="utf8")

    # 1. enlaces internos entre paginas
    for old, new in LINK_MAP.items():
        text = text.replace(old, new)

    # 2. rutas de medios: uploads/ -> assets/ y nombres sin espacios
    for old, new in ASSET_RENAMES.items():
        for variant in (old, urllib.parse.quote(old)):
            text = text.replace(f"uploads/{variant}", f"uploads/{new}")
    text = text.replace("uploads/", "assets/")

    # 3. runtime local en lugar del CDN
    text = text.replace(
        '<script src="./support.js"></script>',
        '<script src="vendor/dc-runtime.js"></script>',
    )

    # 4. fuentes auto-hospedadas: fuera preconnect y link a Google Fonts
    text = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>', "", text)
    text = re.sub(r'\s*<link href="https://fonts\.googleapis\.com/[^"]*" rel="stylesheet">', "", text)

    # 5. idioma
    text = text.replace("<html>", '<html lang="es">', 1)

    # 6. metadatos
    canonical = base_url + ("" if dst_name == "index.html" else dst_name)
    head = HEAD_EXTRA.format(
        title=title, desc=desc, canonical=canonical,
        og_image=base_url + "assets/hero-poster.jpg",
        resources=RESOURCES_JSON,
    )
    anchor = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    assert anchor in text, f"{src_name}: falta el meta viewport"
    text = text.replace(anchor, anchor + "\n" + head, 1)

    (OUT / dst_name).write_text(text, encoding="utf8")


# ------------------------------------------------------------------- extras --
def write_extras(base_url):
    (OUT / ".nojekyll").write_text("", encoding="utf8")

    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base_url}sitemap.xml\n", encoding="utf8")

    urls = "\n".join(
        f"  <url><loc>{base_url}{'' if dst == 'index.html' else dst}</loc>"
        f"<priority>{'1.0' if dst == 'index.html' else '0.7'}</priority></url>"
        for _, dst, _, _ in PAGES)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf8")

    # 404 con el look de marca
    (OUT / "404.html").write_text("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página no encontrada | Interkont</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/fonts/mulish.css">
<style>
:root{--mag:#EA215E;--ink:#131117;--ink-soft:#66646E}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Mulish',system-ui,sans-serif;color:var(--ink);background:#EFEEF2;
  min-height:100vh;display:grid;place-items:center;padding:24px;text-align:center}
.code{font-size:clamp(64px,14vw,132px);font-weight:900;line-height:1;color:var(--mag)}
h1{font-size:clamp(22px,4vw,32px);font-weight:800;margin:12px 0 8px}
p{color:var(--ink-soft);max-width:46ch;margin:0 auto 28px}
a{display:inline-block;background:var(--ink);color:#fff;font-weight:700;text-decoration:none;
  border-radius:100px;padding:14px 28px;transition:transform .2s,box-shadow .3s}
a:hover{transform:translateY(-2px);box-shadow:0 14px 30px -10px rgba(19,17,23,.5)}
</style>
</head>
<body>
<main>
  <div class="code">404</div>
  <h1>Esta página no existe</h1>
  <p>El enlace que seguiste no corresponde a ninguna página del sitio.</p>
  <a href="/">Volver al inicio</a>
</main>
</body>
</html>
""", encoding="utf8")

    (OUT / ".gitignore").write_text(
        ".DS_Store\nThumbs.db\n*.log\n.vscode/\n.idea/\n", encoding="utf8")

    wf = OUT / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "deploy.yml").write_text("""name: Deploy a GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - name: Subir el sitio
        uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
""", encoding="utf8")
    log("extras escritos (.nojekyll, 404, robots, sitemap, workflow)")


def copy_elementor():
    dst = OUT / "elementor"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted((SRC / "elementor").glob("*.json")):
        shutil.copy2(f, dst / f.name)
    shutil.copy2(SRC / "elementor" / "LEEME.md", dst / "LEEME.md")
    shutil.copy2(SRC / "Guia de estilos Interkont.md", OUT / "docs" / "guia-de-estilos.md")
    log("elementor/ y docs/ copiados")


# --------------------------------------------------------------------- main --
def main():
    base_url = os.environ.get("BASE_URL", "")
    if base_url and not base_url.endswith("/"):
        base_url += "/"

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "vendor").mkdir(parents=True)
    (OUT / "docs").mkdir(parents=True)

    log(f"BASE_URL = {base_url or '(relativo)'}")
    copy_assets()
    vendor_fonts()
    build_favicon()

    shutil.copy2(SRC / "support.js", OUT / "vendor" / "dc-runtime.js")
    shutil.copy2("/tmp/react.prod.js", OUT / "vendor" / "react.production.min.js")
    shutil.copy2("/tmp/react-dom.prod.js", OUT / "vendor" / "react-dom.production.min.js")
    log("runtime + React vendorizados")

    for src_name, dst_name, title, desc in PAGES:
        transform_page(src_name, dst_name, title, desc, base_url)
    log(f"paginas generadas: {len(PAGES)}")

    write_extras(base_url)
    copy_elementor()
    print("\nOK ->", OUT)


if __name__ == "__main__":
    main()
