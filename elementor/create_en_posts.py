#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea (o actualiza) en WordPress los articulos en ingles "en-<slug>" a partir de
elementor/en-content/posts/*.json. Cada post EN copia la categoria y la fecha
del post ES equivalente, y reproduce su estructura de bloques (incluido el
parrafo "[KPI] ..."), para que Astro lo renderice con el mismo componente.

Seguro por defecto: sin --apply solo muestra que haria (dry-run). Idempotente.

Uso:
  export WP_URL="https://cms.interkont.co" WP_USER="ikont_admin" WP_APP_PASS="xxxx ..."
  python3 create_en_posts.py            # dry-run
  python3 create_en_posts.py --apply
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


def main():
    print("MODO:", "APPLY (escribe en WP)" if APPLY else "DRY-RUN (no escribe)")
    for f in sorted(glob.glob(os.path.join(HERE, "en-content", "posts", "*.json"))):
        d = json.load(open(f, encoding="utf8"))
        src = request(f"/wp-json/wp/v2/posts?slug={d['es_slug']}&context=edit&status=any")
        if not src:
            print(f"!! {d['slug']}: no existe el post ES '{d['es_slug']}', se omite"); continue
        src = src[0]
        payload = {
            "title": d["title"], "slug": d["slug"], "status": "publish",
            "content": d["content"], "excerpt": f"<p>{d['excerpt']}</p>",
            "categories": src["categories"], "date": src["date"],
        }
        existing = request(f"/wp-json/wp/v2/posts?slug={d['slug']}&context=edit&status=any")
        if existing:
            e = existing[0]
            same = e["content"]["raw"].strip() == d["content"].strip() and e["title"]["raw"] == d["title"]
            print(f"{d['slug']}: existe (id={e['id']}) -> {'sin cambios' if same else 'ACTUALIZA'}")
            if APPLY and not same:
                request(f"/wp-json/wp/v2/posts/{e['id']}", "POST", payload)
                print("  -> guardado")
        else:
            print(f"{d['slug']}: NO existe -> CREA (cat={src['categories']}, fecha={src['date'][:10]})")
            if APPLY:
                r = request("/wp-json/wp/v2/posts", "POST", payload)
                print(f"  -> creado id={r['id']} {r.get('link')}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
