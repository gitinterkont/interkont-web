#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asigna un extracto (excerpt) explicito a cada post del blog, en vez de
depender del extracto automatico de WordPress. Los posts con contenido
"rico" (listas, citas) generaban un extracto automatico que a veces
truncaba a mitad de una etiqueta HTML, rompiendo el layout de la
tarjeta en /blog. El extracto explicito es texto plano seguro (el mismo
parrafo "lead" con el que se armo cada articulo).

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 set_wp_excerpts.py
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

POST_EXCERPTS = {
    14: "Más de 50.000 proyectos y 6.500 millones de dólares supervisados nos dejaron una conclusión incómoda: el problema rara vez es la falta de datos, es la falta de visibilidad sobre ellos.",
    27: "El reconocimiento visual de IK Labs analiza el registro fotográfico de los interventores y valida cascos, chalecos y presencia de personal sin trabajo manual adicional.",
    28: "Más allá del discurso, la trazabilidad es poder responder tres preguntas sobre cada peso invertido: quién lo aprobó, en qué se ejecutó y con qué soporte.",
    29: "El Instrumento de Agregación de Demanda de Colombia Compra Eficiente permite adquirir soluciones desde la Tienda Virtual del Estado sin proceso licitatorio largo.",
    30: "Cómo una entidad nacional pasó de reportes mensuales en hojas de cálculo a un tablero de control con alertas en tiempo real sobre proyectos y contratos.",
    31: "Soberanía de datos, costos predecibles y escalabilidad. Una guía práctica para decidir qué modalidad se ajusta mejor a la realidad de su entidad.",
    32: "La IA conversacional empresarial elimina la dependencia de equipos técnicos para obtener respuestas sobre proyectos, contratos y ejecución presupuestal.",
    33: "COBRA Housing permite verificar el avance de cada mejoramiento de vivienda con registro fotográfico georreferenciado y control de subsidios.",
    34: "Automatizar flujos precontractuales reduce tiempos, elimina errores y deja registro de quién hizo qué en cada etapa del proceso.",
    35: "Cuando la ciudadanía puede consultar el avance de las obras de su territorio, el control deja de ser exclusivo del Estado y se vuelve colectivo.",
}


def auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def set_excerpt(post_id, text):
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}",
        data=json.dumps({"excerpt": text}).encode("utf8"),
        method="POST",
        headers=auth_header(),
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"OK  post {post_id} -> excerpt actualizado ({data['slug']})")
    except urllib.error.HTTPError as e:
        print(f"ERROR post {post_id}: HTTP {e.code}: {e.read().decode()[:300]}")


if __name__ == "__main__":
    for post_id, text in POST_EXCERPTS.items():
        set_excerpt(post_id, text)
