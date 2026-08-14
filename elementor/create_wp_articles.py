#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea los 9 posts de blog que faltaban en WordPress (el articulo.html
original resultó tener 10 articulos distintos bajo un solo #hash, no uno
solo) y renombra el slug del que ya existe ("articulo" -> "once-anos")
para que coincida con el resto.

A diferencia de create_wp_pages.py, aqui SI se migra el cuerpo completo
de cada articulo como bloques nativos de Gutenberg (heading/paragraph/
list/quote), porque la ruta de Astro que los va a consumir es generica
(src/pages/articulo/[slug].astro) y necesita poder renderizar cualquier
post futuro sin cambios de codigo.

Recorte de alcance: los recuadros de KPI ("50K+ Proyectos monitoreados")
de dos articulos no tienen bloque nativo equivalente en WordPress y se
omiten aqui -- se pueden agregar despues como tabla si se necesitan.

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"
  python3 create_wp_articles.py
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

EXISTING_ONCE_ANOS_POST_ID = 14  # el que create_wp_pages.py ya creo con slug "articulo"


def heading_block(text, level):
    attrs = "" if level == 2 else f' {{"level":{level}}}'
    return f'<!-- wp:heading{attrs} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'


def paragraph_block(text):
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def quote_block(text):
    return (
        '<!-- wp:quote -->\n<blockquote class="wp-block-quote">'
        f'<p>{text}</p></blockquote>\n<!-- /wp:quote -->'
    )


def list_block(items):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<!-- wp:list -->\n<ul class="wp-block-list">{lis}</ul>\n<!-- /wp:list -->'


def blocks_to_content(blocks):
    parts = []
    for b in blocks:
        kind = b["type"]
        if kind == "p" or kind == "lead":
            parts.append(paragraph_block(b["text"]))
        elif kind == "list":
            parts.append(list_block(b["items"]))
        elif kind == "quote":
            parts.append(quote_block(b["text"]))
        else:
            parts.append(heading_block(b["text"], int(kind[1])))
    return "\n\n".join(parts)


ARTICLES = [
    {
        "slug": "eye-control",
        "title": "Cómo Eye Control detecta el incumplimiento de normas de seguridad en obra",
        "category": "Inteligencia artificial",
        "blocks": [
            {"type": "lead", "text": "El reconocimiento visual de IK Labs analiza el registro fotográfico de los interventores y valida cascos, chalecos y presencia de personal sin trabajo manual adicional."},
            {"type": "h2", "text": "Del archivo fotográfico al dato"},
            {"type": "p", "text": "Cada obra genera miles de fotografías. Un interventor documenta el avance, sube las imágenes y ahí terminan: en una carpeta que nadie vuelve a abrir salvo cuando hay un problema. Eye Control parte de una idea simple: <b>esas fotos ya contienen la respuesta a preguntas que hoy se responden manualmente</b>."},
            {"type": "h2", "text": "Qué reconoce"},
            {"type": "list", "items": [
                "<b>Elementos de protección personal:</b> cascos, chalecos reflectivos y demás dotación exigida por las normas de salud ocupacional.",
                "<b>Presencia de personal:</b> identifica los momentos en que hay trabajadores en el frente de obra, incluso a partir de cámaras IP.",
                "<b>Calidad del registro:</b> detecta automáticamente fotografías desenfocadas, mal encuadradas o que no aportan evidencia útil.",
            ]},
            {"type": "quote", "text": "Validar el cumplimiento de seguridad deja de ser una revisión muestral y pasa a ser una verificación sobre el cien por ciento del registro."},
            {"type": "h2", "text": "Por qué importa"},
            {"type": "p", "text": "La supervisión tradicional de seguridad industrial es muestral: alguien visita la obra, observa y consigna. Entre visita y visita hay un vacío. Con reconocimiento visual, cada fotografía cargada se convierte en un punto de control, y los incumplimientos recurrentes emergen como patrón, no como anécdota."},
            {"type": "h2", "text": "Cómo se integra"},
            {"type": "p", "text": "Eye Control opera sobre el registro que los interventores ya cargan en COBRA, sin exigir un proceso adicional en campo. El resultado se refleja en el tablero como una capa más de analítica: qué frentes concentran incumplimientos, en qué periodos y con qué contratistas."},
            {"type": "h3", "text": "Un matiz importante"},
            {"type": "p", "text": "La IA no reemplaza el criterio del interventor. Prioriza su atención: en vez de revisar mil imágenes, revisa las cuarenta que el sistema marcó como críticas."},
        ],
    },
    {
        "slug": "trazabilidad",
        "title": "Trazabilidad total: qué significa realmente para una entidad pública",
        "category": "GovTech",
        "blocks": [
            {"type": "lead", "text": "Más allá del discurso, la trazabilidad es poder responder tres preguntas sobre cada peso invertido: quién lo aprobó, en qué se ejecutó y con qué soporte."},
            {"type": "h2", "text": "Una palabra desgastada"},
            {"type": "p", "text": '"Trazabilidad" aparece en casi todos los pliegos y en casi ninguna operación. Se ha vuelto una palabra que tranquiliza sin comprometer a nada concreto. Vale la pena volverla exigible.'},
            {"type": "h2", "text": "Las tres preguntas"},
            {"type": "h3", "text": "¿Quién lo aprobó?"},
            {"type": "p", "text": "Cada movimiento —una adición, un cambio de cronograma, la aprobación de un avance— debe tener un responsable identificable y una fecha. Sin actor y sin momento, no hay trazabilidad; hay historial anónimo."},
            {"type": "h3", "text": "¿En qué se ejecutó?"},
            {"type": "p", "text": "El recurso debe poder seguirse hasta el entregable concreto: este tramo de vía, esta vivienda, este componente del contrato. La agregación presupuestal esconde; el detalle revela."},
            {"type": "h3", "text": "¿Con qué soporte?"},
            {"type": "p", "text": "Todo avance reportado necesita evidencia verificable: registro fotográfico con fecha y ubicación, acta firmada, documento cargado. Una afirmación sin soporte es una intención."},
            {"type": "quote", "text": "Si no puede responder las tres preguntas sobre un contrato en menos de cinco minutos, no tiene trazabilidad: tiene archivo."},
            {"type": "h2", "text": "La prueba práctica"},
            {"type": "list", "items": [
                "Tome un contrato al azar de hace dos años.",
                "Identifique quién aprobó el último pago y con qué evidencia.",
                "Mida cuánto tardó en obtener la respuesta.",
            ]},
            {"type": "p", "text": "Ese tiempo es el indicador real de madurez del control en su entidad."},
        ],
    },
    {
        "slug": "catalogo-iad",
        "title": "Cotizar en el Catálogo IAD: la ruta ágil para adquirir tecnología",
        "category": "Compra pública",
        "blocks": [
            {"type": "lead", "text": "El Instrumento de Agregación de Demanda de Colombia Compra Eficiente permite adquirir soluciones desde la Tienda Virtual del Estado sin proceso licitatorio largo."},
            {"type": "h2", "text": "El problema de tiempo"},
            {"type": "p", "text": "Una entidad identifica una necesidad tecnológica en marzo y contrata en diciembre. No por negligencia: por la duración natural de un proceso licitatorio. Para entonces, la necesidad cambió."},
            {"type": "h2", "text": "Qué es el IAD"},
            {"type": "p", "text": "El Instrumento de Agregación de Demanda es un mecanismo de Colombia Compra Eficiente que agrupa la demanda del Estado y deja proveedores y condiciones ya negociados en un catálogo. La entidad no vuelve a estructurar un proceso: cotiza y emite orden de compra desde la <b>Tienda Virtual del Estado Colombiano</b>."},
            {"type": "h2", "text": "La ruta, paso a paso"},
            {"type": "list", "items": [
                "Ingrese a la Tienda Virtual del Estado Colombiano con las credenciales de su entidad.",
                "Ubique el catálogo correspondiente y las soluciones habilitadas.",
                "Solicite cotización con el alcance que su entidad necesita.",
                "Emita la orden de compra y comience la implementación.",
            ]},
            {"type": "quote", "text": "Semanas en lugar de meses, con las condiciones ya negociadas por Colombia Compra Eficiente."},
            {"type": "h2", "text": "Qué se puede cotizar de Interkont"},
            {"type": "p", "text": "Tanto los agentes de inteligencia artificial de IK Labs como los servicios de implementación y monitoreo de COBRA están disponibles por esta vía. La entidad elige el nivel de implementación que corresponde a su madurez y alcance."},
        ],
    },
    {
        "slug": "ministerio-interior",
        "title": "Ministerio del Interior: monitoreo en vivo de la inversión",
        "category": "Casos de éxito",
        "blocks": [
            {"type": "lead", "text": "Cómo una entidad nacional pasó de reportes mensuales en hojas de cálculo a un tablero de control con alertas en tiempo real sobre proyectos y contratos."},
            {"type": "h2", "text": "El punto de partida"},
            {"type": "p", "text": "La operación se sostenía en un ciclo mensual: cada área consolidaba su información, alguien la unificaba y se producía un informe. El documento describía con precisión un estado que ya había cambiado."},
            {"type": "h2", "text": "Qué se implementó"},
            {"type": "list", "items": [
                "Consolidación de proyectos y contratos en un único tablero de control.",
                "Reporte de avance directamente desde el frente de obra, con evidencia.",
                "Alertas automáticas ante desviaciones de cronograma y contratos sin soporte.",
                "Acceso diferenciado por rol: contratista, interventor, supervisor y alta gerencia.",
            ]},
            {"type": "quote", "text": "El cambio de fondo no fue tecnológico: fue que la conversación dejó de ser sobre qué pasó y pasó a ser sobre qué hacemos."},
            {"type": "h2", "text": "Resultados observables"},
            {"type": "p", "text": "87% de ejecución con seguimiento en vivo, más de 412 alertas gestionadas por periodo, y 98.4% de trazabilidad documental."},
            {"type": "h2", "text": "La lección"},
            {"type": "p", "text": "La adopción no depende del software sino del compromiso de todos los actores en alimentarlo. Cuando el contratista entiende que reportar bien acelera su propio pago, el sistema se sostiene solo."},
        ],
    },
    {
        "slug": "onpremise-saas",
        "title": "On-Premise o SaaS: cómo elegir el modelo de licenciamiento de COBRA",
        "category": "Producto",
        "blocks": [
            {"type": "lead", "text": "Soberanía de datos, costos predecibles y escalabilidad. Una guía práctica para decidir qué modalidad se ajusta mejor a la realidad de su entidad."},
            {"type": "h2", "text": "No hay una respuesta universal"},
            {"type": "p", "text": "La decisión no es técnica sino institucional: depende de la política de datos de la entidad, de su capacidad de infraestructura y de cómo estén estructurados sus presupuestos."},
            {"type": "h2", "text": "Licencia perpetua On-Premise"},
            {"type": "p", "text": "Con un pago único la entidad adquiere el derecho de uso indefinido y el software se instala en su propia infraestructura. No hay costos recurrentes de licenciamiento."},
            {"type": "list", "items": [
                "Control total y soberanía sobre los datos.",
                "Costos fijos y predecibles, sin renovación anual.",
                "Requiere infraestructura propia y equipo técnico para operarla.",
                "Incluye actualizaciones menores y parches de seguridad.",
            ]},
            {"type": "h2", "text": "SaaS en nube dedicada"},
            {"type": "p", "text": "Un ambiente aislado con infraestructura dedicada, gestionado íntegramente por Interkont."},
            {"type": "list", "items": [
                "Almacenamiento y usuarios ilimitados.",
                "Escalabilidad de decenas a miles de proyectos.",
                "Soporte 24/7 y disponibilidad garantizada del 99.9%.",
                "Sin inversión en servidores ni administración de infraestructura.",
            ]},
            {"type": "quote", "text": "Si su política de datos exige que la información no salga de la entidad, la decisión ya está tomada. Si su prioridad es empezar rápido, también."},
            {"type": "h2", "text": "Tres preguntas para decidir"},
            {"type": "list", "items": [
                "¿Su marco normativo interno permite alojar la información fuera de la entidad?",
                "¿Cuenta con equipo técnico para administrar servidores y respaldos?",
                "¿Su presupuesto favorece una inversión única o un gasto recurrente?",
            ]},
        ],
    },
    {
        "slug": "datawiz",
        "title": "DataWiz AI: preguntarle a sus datos en lenguaje natural",
        "category": "Inteligencia artificial",
        "blocks": [
            {"type": "lead", "text": "La IA conversacional empresarial elimina la dependencia de equipos técnicos para obtener respuestas sobre proyectos, contratos y ejecución presupuestal."},
            {"type": "h2", "text": "El cuello de botella invisible"},
            {"type": "p", "text": "En casi toda entidad hay dos o tres personas que saben construir la consulta correcta. Toda pregunta relevante pasa por ellas. No es un problema de talento: es un cuello de botella estructural que ralentiza cada decisión."},
            {"type": "h2", "text": "Qué hace DataWiz"},
            {"type": "p", "text": "Conecta de forma segura los datos estructurados y no estructurados de la organización con modelos avanzados de lenguaje natural, para que cualquier persona autorizada pueda preguntar sin conocimientos técnicos y obtener respuestas en texto, tablas o gráficos."},
            {"type": "h2", "text": "Seguridad primero"},
            {"type": "list", "items": [
                "Control granular RBAC/ABAC: cada usuario consulta solo lo que le corresponde.",
                "Cifrado TLS 1.3 en tránsito y AES-256 en reposo.",
                "Sus datos <b>no</b> se usan para entrenar modelos públicos.",
                "Modelos empresariales vía API, con posibilidad de integrar otros proveedores.",
            ]},
            {"type": "quote", "text": "La pregunta correcta ya no requiere saber SQL. Requiere saber qué se quiere entender."},
            {"type": "h2", "text": "COBRA IA"},
            {"type": "p", "text": "El mismo motor, integrado directamente en COBRA Corporate y aplicado a los datos de proyectos, contratos y ejecución que la plataforma ya administra."},
        ],
    },
    {
        "slug": "vivienda",
        "title": "Vivienda: seguimiento unidad por unidad con evidencia en sitio",
        "category": "Casos de éxito",
        "blocks": [
            {"type": "lead", "text": "COBRA Housing permite verificar el avance de cada mejoramiento de vivienda con registro fotográfico georreferenciado y control de subsidios."},
            {"type": "h2", "text": "El reto de la escala menuda"},
            {"type": "p", "text": "Un programa de mejoramiento de vivienda no es una obra grande: son miles de obras pequeñas, dispersas geográficamente, cada una con su beneficiario y su subsidio. El control agregado no sirve; hay que poder mirar una casa concreta."},
            {"type": "h2", "text": "Cómo se resuelve"},
            {"type": "list", "items": [
                "Avance registrado por unidad: cada vivienda, torre o etapa tiene su propio estado.",
                "Georreferenciación: cada intervención ubicada sobre el mapa.",
                "Evidencia fotográfica con fecha y responsable.",
                "Trazabilidad de subsidios y desembolsos por beneficiario.",
            ]},
            {"type": "quote", "text": 'Cuando cada vivienda tiene su expediente digital, la pregunta "¿en qué se gastó el subsidio?" tiene respuesta inmediata.'},
            {"type": "h2", "text": "Modo offline"},
            {"type": "p", "text": "Buena parte de estos programas ocurre donde no hay señal. Las aplicaciones móviles capturan el avance sin conexión y sincronizan automáticamente al recuperarla, para que la falta de red no se convierta en falta de evidencia."},
            {"type": "h2", "text": "Impacto en la relación con el beneficiario"},
            {"type": "p", "text": "La transparencia también es hacia abajo: cuando la familia beneficiaria puede verificar el estado de su intervención, disminuye la desconfianza y las reclamaciones se vuelven concretas y resolubles."},
        ],
    },
    {
        "slug": "bpm",
        "title": "De trámite en papel a proceso digital trazable con COBRA BPM",
        "category": "Producto",
        "blocks": [
            {"type": "lead", "text": "Automatizar flujos precontractuales reduce tiempos, elimina errores y deja registro de quién hizo qué en cada etapa del proceso."},
            {"type": "h2", "text": "El trámite invisible"},
            {"type": "p", "text": "Antes de que exista un contrato hay decenas de pasos: estudios previos, revisiones, aprobaciones, firmas. Ese recorrido rara vez está medido. Nadie sabe con precisión dónde se demora el proceso, solo que se demora."},
            {"type": "h2", "text": "Qué permite COBRA BPM"},
            {"type": "list", "items": [
                "Modelar flujos de aprobación y trámites a la medida de la entidad.",
                "Automatizar tareas repetitivas para reducir tiempos y errores.",
                "Registrar quién hizo qué y cuándo en cada etapa.",
                "Medir cuellos de botella con indicadores de desempeño reales.",
            ]},
            {"type": "quote", "text": "Digitalizar un proceso no es escanear el papel: es que el proceso deje rastro medible."},
            {"type": "h2", "text": "Por dónde empezar"},
            {"type": "p", "text": "Recomendamos comenzar por un solo flujo de alto volumen —normalmente el precontractual— medirlo durante un trimestre y expandir a partir de esa evidencia. La automatización total desde el primer día suele fracasar por resistencia organizacional."},
        ],
    },
    {
        "slug": "participacion",
        "title": "Participación ciudadana: la vigilancia que multiplica la transparencia",
        "category": "GovTech",
        "blocks": [
            {"type": "lead", "text": "Cuando la ciudadanía puede consultar el avance de las obras de su territorio, el control deja de ser exclusivo del Estado y se vuelve colectivo."},
            {"type": "h2", "text": "El control no escala solo desde adentro"},
            {"type": "p", "text": "Ninguna entidad tiene supervisores suficientes para vigilar cada obra todos los días. Pero cada obra tiene vecinos que pasan frente a ella a diario. Esa asimetría es una oportunidad."},
            {"type": "h2", "text": "Qué significa habilitar la participación"},
            {"type": "list", "items": [
                "Publicar el estado real de avance de las obras del territorio.",
                "Permitir que la ciudadanía reporte observaciones asociadas a un proyecto concreto.",
                "Cerrar el ciclo: que cada observación tenga respuesta trazable.",
            ]},
            {"type": "quote", "text": "La transparencia que no se puede consultar no es transparencia: es publicación."},
            {"type": "h2", "text": "Las condiciones para que funcione"},
            {"type": "p", "text": 'La participación exige información comprensible. Publicar un CDP y un número de contrato no informa a nadie. Publicar "esta vía, este avance, esta fecha prevista, esta evidencia" sí. La calidad del dato determina si el mecanismo se usa o se abandona.'},
            {"type": "h2", "text": "El efecto secundario"},
            {"type": "p", "text": "Cuando el contratista sabe que su avance es público, la calidad del reporte mejora sin necesidad de sanción. La visibilidad es, en sí misma, un incentivo."},
        ],
    },
]


def auth_header():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def request(method, path, payload):
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/{path}",
        data=json.dumps(payload).encode("utf8"),
        method=method,
        headers=auth_header(),
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def rename_existing_once_anos():
    try:
        data = request("POST", f"posts/{EXISTING_ONCE_ANOS_POST_ID}", {"slug": "once-anos"})
        print(f"OK  renombrado post {EXISTING_ONCE_ANOS_POST_ID} -> slug={data['slug']}  {data['link']}")
    except urllib.error.HTTPError as e:
        print(f"ERROR renombrando post {EXISTING_ONCE_ANOS_POST_ID}: HTTP {e.code}: {e.read().decode()[:300]}")


def create_article(article):
    try:
        data = request("POST", "posts", {
            "title": article["title"],
            "slug": article["slug"],
            "status": "draft",
            "content": blocks_to_content(article["blocks"]),
        })
        print(f"OK  [post] {article['slug']:20s} -> id={data['id']}  {data['link']}")
    except urllib.error.HTTPError as e:
        print(f"ERROR [post] {article['slug']:20s} -> HTTP {e.code}: {e.read().decode()[:300]}")


if __name__ == "__main__":
    rename_existing_once_anos()
    for article in ARTICLES:
        create_article(article)
