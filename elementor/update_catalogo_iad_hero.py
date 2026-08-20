#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reemplaza el titulo y el parrafo del hero de la pagina "catalogo-iad" en
WordPress. Hoy siguen diciendo "Esta seccion esta en obra" (el texto de
marcador de posicion con el que se creo la pagina originalmente) -- pero
el Catalogo IAD ya es funcional (catalogo + simulador de cotizacion), asi
que ese texto quedo desactualizado y confunde al visitante.

Solo toca esos dos bloques (H1 y el parrafo inmediatamente despues); no
toca el resto del contenido de la pagina (por ejemplo el parrafo de marca
del footer).

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 update_catalogo_iad_hero.py
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

OLD_H1 = "Esta sección está en obra"
OLD_P = (
    "Estamos preparando el contenido del <b>Catálogo IAD</b> para que pueda cotizar nuestras "
    "soluciones directamente desde la Tienda Virtual del Estado Colombiano. Muy pronto disponible."
)
NEW_H1 = "Explore el catálogo y arme su cotización"
NEW_P = (
    "Todos nuestros productos y servicios con su código, unidad de medida y precio. Simule la "
    "cotización de su entidad y descárguela en PDF, lista para la Tienda Virtual del Estado."
)


def heading_block(text, level=1):
    attrs = "" if level == 2 else f' {{"level":{level}}}'
    return f'<!-- wp:heading{attrs} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'


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
    pages = request("/wp-json/wp/v2/pages?slug=catalogo-iad&context=edit")
    if not pages:
        sys.exit("ERROR: no se encontro ninguna pagina con slug 'catalogo-iad'.")
    page = pages[0]
    content = page["content"]["raw"]

    old_h1_block = heading_block(OLD_H1)
    old_p_block = paragraph_block(OLD_P)

    if old_h1_block not in content or old_p_block not in content:
        sys.exit(
            "ERROR: no se encontraron los bloques exactos de 'en obra' -- puede que ya se hayan "
            "editado a mano en wp-admin. No se modifico nada."
        )

    content = content.replace(old_h1_block, heading_block(NEW_H1), 1)
    content = content.replace(old_p_block, paragraph_block(NEW_P), 1)

    result = request(f"/wp-json/wp/v2/pages/{page['id']}", method="POST", body={"content": content})
    print(f"OK  catalogo-iad (id={page['id']}) actualizado -> {result.get('link')}")
    print(f"  H1: {NEW_H1!r}")
    print(f"  P:  {NEW_P!r}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
