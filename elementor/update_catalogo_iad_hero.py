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
import re
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

# Se busca por el texto en si (con un regex tolerante a atributos/clases
# distintos en el tag), no por el bloque completo con su comentario de
# Gutenberg -- asi funciona aunque WordPress haya guardado el bloque con
# una forma ligeramente distinta a la que uso el script que creo la pagina.
OLD_H1_TEXT = "Esta sección está en obra"
OLD_P_MARKER = "Estamos preparando el contenido"
NEW_H1 = "Explore el catálogo y arme su cotización"
NEW_P = (
    "Todos nuestros productos y servicios con su código, unidad de medida y precio. Simule la "
    "cotización de su entidad y descárguela en PDF, lista para la Tienda Virtual del Estado."
)

H1_PATTERN = re.compile(r"(<h1\b[^>]*>)(.*?)(</h1>)", re.DOTALL)
P_PATTERN = re.compile(r"(<p\b[^>]*>)(.*?)(</p>)", re.DOTALL)


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

    h1_replaced = [False]
    def h1_sub(m):
        if OLD_H1_TEXT in m.group(2):
            h1_replaced[0] = True
            return m.group(1) + NEW_H1 + m.group(3)
        return m.group(0)

    p_replaced = [False]
    def p_sub(m):
        if OLD_P_MARKER in m.group(2):
            p_replaced[0] = True
            return m.group(1) + NEW_P + m.group(3)
        return m.group(0)

    new_content = H1_PATTERN.sub(h1_sub, content, count=1)
    new_content = P_PATTERN.sub(p_sub, new_content, count=1)

    if not h1_replaced[0] or not p_replaced[0]:
        print("ERROR: no se encontro el texto esperado -- no se modifico nada. Diagnostico:")
        h1s = H1_PATTERN.findall(content)
        ps = P_PATTERN.findall(content)
        print(f"  H1 encontrado en la pagina ({len(h1s)}): {[h[1][:80] for h in h1s]}")
        print(f"  Primeros parrafos ({len(ps)}): {[p[1][:80] for p in ps[:3]]}")
        sys.exit(1)

    result = request(f"/wp-json/wp/v2/pages/{page['id']}", method="POST", body={"content": new_content})
    print(f"OK  catalogo-iad (id={page['id']}) actualizado -> {result.get('link')}")
    print(f"  H1: {NEW_H1!r}")
    print(f"  P:  {NEW_P!r}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
