#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea (o actualiza) en WordPress las paginas en ingles "en-<slug>" a partir de
elementor/en-content/*.json. Cada JSON trae {"title","slug","blocks":[...]} en el
mismo orden de indices que usa Astro (blocks[n]) en las paginas /en/*.

Seguro por defecto: sin --apply solo muestra que haria (dry-run).
Idempotente: si la pagina ya existe actualiza su contenido en lugar de duplicarla.

Uso:
  export WP_URL="https://cms.interkont.co" WP_USER="ikont_admin" WP_APP_PASS="xxxx ..."
  python3 create_en_pages.py            # dry-run
  python3 create_en_pages.py --apply
"""
import os, sys, json, glob, base64, urllib.request, urllib.error

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASS = os.environ.get("WP_APP_PASS")
APPLY = "--apply" in sys.argv
if not all([WP_URL, WP_USER, WP_APP_PASS]):
    sys.exit("ERROR: define WP_URL, WP_USER y WP_APP_PASS como variables de entorno.")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
HERE = os.path.dirname(os.path.abspath(__file__))


def request(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{WP_URL}{path}",
        data=json.dumps(body).encode("utf8") if body is not None else None,
        method=method, headers={"Content-Type": "application/json"})
    req.add_header("Authorization", f"Basic {AUTH}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def block(b):
    if b["type"] == "heading":
        lv = b.get("level", 2)
        return f'<!-- wp:heading {{"level":{lv}}} -->\n<h{lv} class="wp-block-heading">{b["content"]}</h{lv}>\n<!-- /wp:heading -->'
    return f'<!-- wp:paragraph -->\n<p>{b["content"]}</p>\n<!-- /wp:paragraph -->'


def main():
    print("MODO:", "APPLY (escribe en WP)" if APPLY else "DRY-RUN (no escribe)")
    for f in sorted(glob.glob(os.path.join(HERE, "en-content", "*.json"))):
        d = json.load(open(f, encoding="utf8"))
        content = "\n\n".join(block(b) for b in d["blocks"])
        existing = request(f"/wp-json/wp/v2/pages?slug={d['slug']}&context=edit&status=any")
        if existing:
            pid = existing[0]["id"]
            same = existing[0]["content"]["raw"].strip() == content.strip()
            print(f"{d['slug']}: existe (id={pid}) -> {'sin cambios' if same else 'ACTUALIZA'} ({len(d['blocks'])} bloques)")
            if APPLY and not same:
                request(f"/wp-json/wp/v2/pages/{pid}", "POST", {"title": d["title"], "content": content})
                print("  -> guardado")
        else:
            print(f"{d['slug']}: NO existe -> CREA publicada ({len(d['blocks'])} bloques)")
            if APPLY:
                r = request("/wp-json/wp/v2/pages", "POST",
                            {"title": d["title"], "slug": d["slug"], "status": "publish", "content": content})
                print(f"  -> creada id={r['id']} {r.get('link')}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
