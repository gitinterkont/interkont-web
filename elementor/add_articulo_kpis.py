#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agrega el parrafo "[KPI] ..." (la fila de 3 estadisticas que ahora
src/pages/articulo/[slug].astro sabe reconocer y renderizar como .kpirow)
a los 3 articulos que lo necesitan: "once-anos", "ministerio-interior" y
"datawiz". No toca ningun otro contenido de esos posts, salvo un ajuste
puntual en "once-anos" (ver mas abajo).

Que hace en cada articulo, y por que:

- once-anos: inserta el parrafo KPI justo despues del lead y antes de
  "El dato existe, la visibilidad no". Ademas, convierte el parrafo
  "El problema del control publico no es la ausencia de informacion..."
  de parrafo normal a bloque de Cita (wp:quote) -- este articulo se creo
  con create_wp_pages.py, antes de que existiera el bloque de cita en
  ese script, asi que le faltaba ese tratamiento que los otros 9
  articulos ya tienen.
- ministerio-interior: REEMPLAZA el parrafo "87% de ejecucion con
  seguimiento en vivo..." (que hoy repite en prosa las mismas 3 cifras)
  por el parrafo KPI, para no duplicar la informacion.
- datawiz: inserta el parrafo KPI justo despues del parrafo "Conecta de
  forma segura los datos..." y antes de "Seguridad primero".

Si el texto ancla de algun articulo no coincide exactamente con el
contenido real en WordPress (por ejemplo, si alguien ya lo edito a mano),
el script avisa con ERROR y no toca ese articulo -- nunca inserta a
ciegas.

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 add_articulo_kpis.py
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


def get_post_by_slug(slug):
    posts = request(f"/wp-json/wp/v2/posts?slug={slug}&context=edit")
    if not posts:
        raise RuntimeError(f"No se encontro ningun post con slug '{slug}'.")
    return posts[0]


def kpi_paragraph_block(text):
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def quote_block(text):
    return (
        '<!-- wp:quote -->\n<blockquote class="wp-block-quote">'
        f'<p>{text}</p></blockquote>\n<!-- /wp:quote -->'
    )


def paragraph_block(text):
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def insert_after(content, anchor_block, new_block, label):
    if anchor_block not in content:
        print(f"ERROR [{label}] no se encontro el bloque ancla exacto -- no se modifico nada. "
              f"Puede que el contenido ya haya sido editado a mano en wp-admin.")
        return None
    return content.replace(anchor_block, anchor_block + "\n\n" + new_block, 1)


def replace_block(content, old_block, new_block, label):
    if old_block not in content:
        print(f"ERROR [{label}] no se encontro el bloque a reemplazar -- no se modifico nada. "
              f"Puede que el contenido ya haya sido editado a mano en wp-admin.")
        return None
    return content.replace(old_block, new_block, 1)


def update_post(post_id, new_content, label):
    result = request(f"/wp-json/wp/v2/posts/{post_id}", method="POST", body={"content": new_content})
    print(f"OK  [{label}] post {post_id} actualizado -> {result.get('link')}")


def process_once_anos():
    label = "once-anos"
    post = get_post_by_slug(label)
    content = post["content"]["raw"]

    lead_block = paragraph_block(
        "Más de 50.000 proyectos y 6.500 millones de dólares supervisados nos dejaron una "
        "conclusión incómoda: el problema rara vez es la falta de datos, es la falta de "
        "visibilidad sobre ellos."
    )
    kpi_block = kpi_paragraph_block(
        "[KPI] 50K+::Proyectos monitoreados | $6.5B::Dólares controlados | 11::Años de operación"
    )
    content2 = insert_after(content, lead_block, kpi_block, label)
    if content2 is None:
        return
    content = content2

    old_quote_p = paragraph_block(
        "El problema del control público no es la ausencia de información. Es que la "
        "información llega tarde y fragmentada a quien decide."
    )
    new_quote = quote_block(
        "El problema del control público no es la ausencia de información. Es que la "
        "información llega tarde y fragmentada a quien decide."
    )
    content2 = replace_block(content, old_quote_p, new_quote, label)
    if content2 is None:
        # seguimos igual con el KPI ya insertado, avisando que la cita no se pudo convertir
        update_post(post["id"], content, label + " (solo KPI, sin convertir la cita)")
        return
    content = content2

    update_post(post["id"], content, label)


def process_ministerio_interior():
    label = "ministerio-interior"
    post = get_post_by_slug(label)
    content = post["content"]["raw"]

    old_prose = paragraph_block(
        "87% de ejecución con seguimiento en vivo, más de 412 alertas gestionadas por periodo, "
        "y 98.4% de trazabilidad documental."
    )
    kpi_block = kpi_paragraph_block(
        "[KPI] 87%::Ejecución con seguimiento en vivo | +412::Alertas gestionadas por periodo | "
        "98.4%::Trazabilidad documental"
    )
    content2 = replace_block(content, old_prose, kpi_block, label)
    if content2 is None:
        return
    update_post(post["id"], content2, label)


def process_datawiz():
    label = "datawiz"
    post = get_post_by_slug(label)
    content = post["content"]["raw"]

    anchor_p = paragraph_block(
        "Conecta de forma segura los datos estructurados y no estructurados de la "
        "organización con modelos avanzados de lenguaje natural, para que cualquier persona "
        "autorizada pueda preguntar sin conocimientos técnicos y obtener respuestas en texto, "
        "tablas o gráficos."
    )
    kpi_block = kpi_paragraph_block(
        "[KPI] 500M::Tokens de escalabilidad | 50K::Consultas mensuales | 99.5%::Disponibilidad (ANS)"
    )
    content2 = insert_after(content, anchor_p, kpi_block, label)
    if content2 is None:
        return
    update_post(post["id"], content2, label)


if __name__ == "__main__":
    try:
        process_once_anos()
        process_ministerio_interior()
        process_datawiz()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR HTTP {e.code}: {e.read().decode()[:500]}")
    except RuntimeError as e:
        sys.exit(f"ERROR: {e}")
