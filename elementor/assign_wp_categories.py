#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asigna categorias reales de WordPress a los posts del blog (se me olvido
hacerlo en create_wp_articles.py). Crea la categoria si no existe y la
asigna al post correspondiente.

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 assign_wp_categories.py
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

# post_id -> nombre de categoria (mismas que en create_wp_articles.py)
POST_CATEGORIES = {
    14: "GovTech",                       # once-anos (renombrado por create_wp_articles.py)
    27: "Inteligencia artificial",        # eye-control
    28: "GovTech",                        # trazabilidad
    29: "Compra pública",                 # catalogo-iad
    30: "Casos de éxito",                 # ministerio-interior
    31: "Producto",                       # onpremise-saas
    32: "Inteligencia artificial",        # datawiz
    33: "Casos de éxito",                 # vivienda
    34: "Producto",                       # bpm
    35: "GovTech",                        # participacion
}


def auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def request(method, path, payload=None):
    data = json.dumps(payload).encode("utf8") if payload is not None else None
    req = urllib.request.Request(f"{WP_URL}/wp-json/wp/v2/{path}", data=data, method=method, headers=auth_header())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_or_create_category(name):
    try:
        return request("POST", "categories", {"name": name})["id"]
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        if body.get("code") == "term_exists":
            return body["data"]["term_id"]
        raise


def main():
    cache = {}
    for post_id, cat_name in POST_CATEGORIES.items():
        if cat_name not in cache:
            cache[cat_name] = get_or_create_category(cat_name)
            print(f"categoria '{cat_name}' -> id={cache[cat_name]}")
        cat_id = cache[cat_name]
        try:
            data = request("POST", f"posts/{post_id}", {"categories": [cat_id]})
            print(f"OK  post {post_id} -> categoria '{cat_name}' asignada")
        except urllib.error.HTTPError as e:
            print(f"ERROR post {post_id}: HTTP {e.code}: {e.read().decode()[:300]}")


if __name__ == "__main__":
    main()
