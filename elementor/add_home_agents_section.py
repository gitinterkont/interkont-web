#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agrega al final del contenido de la pagina "home" (WordPress) dos bloques
nativos de Gutenberg -- un titulo (H2) y un parrafo -- para que el encabezado
y la intro de la nueva seccion "Motor de inteligencia" del landing sean
editables desde wp-admin. El resto de la seccion (las 6 tarjetas de agente,
la barra de orquestacion, el pie de proveedores) vive fijo en el codigo de
Astro, igual que las demas tarjetas estructuradas del sitio.

No borra ni reordena el contenido existente de la pagina: solo agrega estos
dos bloques nuevos al final. En Astro se leen por posicion como
blocks[18] (titulo) y blocks[19] (parrafo).

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"   # Application Password
  python3 add_home_agents_section.py
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASS = os.environ.get("WP_APP_PASS")

if not all([WP_URL, WP_USER, WP_APP_PASS]):
    sys.exit("ERROR: define WP_URL, WP_USER y WP_APP_PASS como variables de entorno.")

AUTH_TOKEN = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()

NEW_HEADING = "Los agentes que potencian la plataforma"
NEW_PARAGRAPH = (
    "No es una sola IA genérica: es una arquitectura de agentes especializados "
    "que trabajan en conjunto, cada uno resolviendo lo que hace mejor."
)


def heading_block(text, level=2):
    return f'<!-- wp:heading -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'


def paragraph_block(text):
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def request(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{WP_URL}{path}",
        data=json.dumps(body).encode("utf8") if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    req.add_header("Authorization", f"Basic {AUTH_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    pages = request("/wp-json/wp/v2/pages?slug=home&context=edit")
    if not pages:
        sys.exit("ERROR: no se encontro ninguna pagina con slug 'home'.")
    page = pages[0]
    page_id = page["id"]
    current_content = page["content"]["raw"]

    if "Motor de inteligencia" in current_content:
        sys.exit(
            "La pagina 'home' ya tiene contenido con 'Motor de inteligencia' -- "
            "revisa manualmente antes de correr este script de nuevo, para no duplicar bloques."
        )

    new_blocks = "\n\n".join([heading_block(NEW_HEADING), paragraph_block(NEW_PARAGRAPH)])
    updated_content = current_content.rstrip() + "\n\n" + new_blocks

    result = request(
        f"/wp-json/wp/v2/pages/{page_id}",
        method="POST",
        body={"content": updated_content},
    )
    print(f"OK  home (id={page_id}) actualizado -> {result.get('link')}")
    print("Nuevos bloques agregados al final del contenido:")
    print(f"  - H2: {NEW_HEADING!r}")
    print(f"  - P:  {NEW_PARAGRAPH!r}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
