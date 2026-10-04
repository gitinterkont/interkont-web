#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actualiza en WordPress los textos de la actualizacion GovTech (quince anos,
IA-first, CTAs de demo, cifras 200K/100K/20B) en home, cobra, panal, ik-labs,
nosotros, el articulo "once-anos" y las descripciones del menu.

Seguro por defecto: sin --apply solo muestra el diff (dry-run). Cada cambio es
un reemplazo exacto sobre el contenido crudo (raw); si el texto viejo no se
encuentra se reporta y se omite (idempotente: si el nuevo ya esta, dice OK).

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"   # Application Password
  python3 update_govtech_texts.py            # dry-run
  python3 update_govtech_texts.py --apply    # escribe en WP
"""
import os, sys, json, base64, urllib.request, urllib.error

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASS = os.environ.get("WP_APP_PASS")
APPLY = "--apply" in sys.argv
if not all([WP_URL, WP_USER, WP_APP_PASS]):
    sys.exit("ERROR: define WP_URL, WP_USER y WP_APP_PASS como variables de entorno.")
AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()

# (tipo, slug, [(viejo, nuevo), ...])
CHANGES = [
    ("pages", "home", [
        ("Once años monitoreando proyectos y contratos, ahora con inteligencia artificial.",
         "Más de quince años monitoreando proyectos y contratos, ahora con inteligencia artificial."),
    ]),
    ("pages", "cobra", [
        ("La nueva manera de monitorear contratos, proyectos y obras. En cualquier momento y lugar, con control visual y en tiempo real.",
         "La nueva manera de monitorear contratos, proyectos y obras: una plataforma IA-first donde agentes inteligentes leen la evidencia del terreno y devuelven decisiones. En cualquier momento y lugar, con control visual y en tiempo real."),
        ("Conózcanos y vea cómo COBRA le da visibilidad total de proyectos y contratos en tiempo real.",
         "Solicite una demo y vea cómo COBRA le da visibilidad total de proyectos y contratos en tiempo real."),
    ]),
    ("pages", "panal", [
        ("todas las ayudas que una población pueda necesitar.</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:heading",
         "todas las ayudas que una población pueda necesitar, con agentes de IA que validan, priorizan y verifican cada caso.</p>\n<!-- /wp:paragraph -->\n\n<!-- wp:heading"),
        ("Conózcanos y descubra cómo canalizar ayudas con trazabilidad total.",
         "Solicite una demo de PANAL y conozca cómo canalizar ayudas con trazabilidad total."),
        (">Simplificamos la manera de ayudar</h2>",
         ">Simplificamos la manera de <span class=\"accent\">ayudar</span></h2>"),
    ]),
    ("pages", "ik-labs", [
        ("somos agentic AI-first.", "somos agentic IA-first."),
        (">Somos agentic AI-first</h2>", ">Somos <span class=\"accent\">agentic IA-first</span></h2>"),
    ]),
    ("pages", "nosotros", [
        ("Once años de experiencia focalizada", "Quince años de experiencia focalizada"),
        (">Una empresa global de software</h2>", ">Una empresa <span class=\"accent\">global</span> de software</h2>"),
        (">Un equipo que fija el estándar</h2>", ">Un equipo que fija el <span class=\"accent\">estándar</span></h2>"),
        (">Once años de impacto medible</h2>", ">Quince años de impacto medible</h2>"),
    ]),
    ("posts", "once-anos", [
        ("Once años monitoreando lo público: lo que aprendimos sobre la inversión del Estado",
         "Más de quince años monitoreando lo público: lo que aprendimos sobre la inversión del Estado"),
        ("Más de 50.000 proyectos y 6.500 millones de dólares supervisados",
         "Más de 200.000 proyectos y 20.000 millones de dólares supervisados"),
        ("[KPI] 50K+::Proyectos monitoreados | $6.5B::Dólares controlados | 11::Años de operación",
         "[KPI] 200K::Proyectos monitoreados | $20B::Dólares controlados | 15::Años de operación"),
    ]),
]

MENU = {  # label -> (descripcion vieja, nueva)
    "COBRA": "IA-first · Monitoreo de inversión pública en tiempo real",
    "PANAL": "IA-first · Asistencia a necesidades de ayudas localizadas",
}


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
    for kind, slug, pairs in CHANGES:
        items = request(f"/wp-json/wp/v2/{kind}?slug={slug}&context=edit&status=any")
        if not items:
            print(f"!! {kind}/{slug}: no encontrado"); continue
        item = items[0]
        raw = item["content"]["raw"]
        title = item["title"]["raw"]
        body = {}
        print(f"\n== {kind}/{slug} (id={item['id']})")
        for old, new in pairs:
            if old in raw:
                raw = raw.replace(old, new, 1)
                print(f"  CAMBIA  {old[:70]!r}\n      ->  {new[:70]!r}")
            elif new in raw:
                print(f"  OK ya aplicado: {new[:70]!r}")
            else:
                print(f"  !! NO ENCONTRADO: {old[:70]!r}")
        if kind == "posts":
            old_t = "Once años monitoreando lo público"
            if title.startswith(old_t):
                body["title"] = title.replace(old_t, "Más de quince años monitoreando lo público", 1)
                print(f"  CAMBIA título -> {body['title'][:70]!r}")
            exc = item["excerpt"]["raw"]
            if "50.000 proyectos" in exc:
                body["excerpt"] = exc.replace("Más de 50.000 proyectos y 6.500 millones de dólares",
                                              "Más de 200.000 proyectos y 20.000 millones de dólares")
                print("  CAMBIA excerpt")
        if raw != item["content"]["raw"]:
            body["content"] = raw
        if body and APPLY:
            request(f"/wp-json/wp/v2/{kind}/{item['id']}", "POST", body)
            print("  -> guardado")

    print("\n== menu")
    try:
        menu_items = request("/wp-json/wp/v2/menu-items?per_page=100&context=edit")
        for mi in menu_items:
            label = (mi.get("title") or {}).get("raw", "")
            if label in MENU:
                cur = mi.get("description", "")
                if cur == MENU[label]:
                    print(f"  OK {label}: ya aplicado")
                else:
                    print(f"  CAMBIA {label}: {cur!r} -> {MENU[label]!r}")
                    if APPLY:
                        request(f"/wp-json/wp/v2/menu-items/{mi['id']}", "POST", {"description": MENU[label]})
                        print("  -> guardado")
    except urllib.error.HTTPError as e:
        print(f"  !! menu-items no disponible (HTTP {e.code}); editar a mano en Apariencia > Menús")

    print("\nNota: tras --apply, el sitio se regenera con el dispatch 'wordpress-published' "
          "o lanzando el workflow de deploy a mano. El SEO title del articulo (Yoast) se revisa en wp-admin.")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
