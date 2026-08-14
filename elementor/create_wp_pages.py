#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea las 9 paginas del sitio en WordPress (headless, cms.interkont.co) via
la API REST, con el contenido narrativo "plano" (titulos y parrafos) de cada
pagina como bloques nativos de Gutenberg. Todo lo demas -- grids de tarjetas,
tablero, marquesina, slider de casos, header/footer -- NO se crea aqui:
vive en el frontend de Astro como diseno/animacion, no como contenido de WP.

Uso:
  export WP_URL="https://cms.interkont.co"
  export WP_USER="ikont_admin"
  export WP_APP_PASS="xxxx xxxx xxxx xxxx xxxx xxxx"   # Application Password
  python3 create_wp_pages.py

Las paginas se crean en estado "draft" -- revisalas y publicalas tu mismo
desde el admin de WordPress.
"""
import os
import sys
import json
import urllib.request
import urllib.error

WP_URL = os.environ.get("WP_URL", "").rstrip("/")
WP_USER = os.environ.get("WP_USER")
WP_APP_PASS = os.environ.get("WP_APP_PASS")

if not all([WP_URL, WP_USER, WP_APP_PASS]):
    sys.exit("ERROR: define WP_URL, WP_USER y WP_APP_PASS como variables de entorno.")


def heading_block(text, level):
    attrs = "" if level == 2 else f' {{"level":{level}}}'
    return f'<!-- wp:heading{attrs} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'


def paragraph_block(text):
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'


def blocks_to_content(blocks):
    parts = []
    for b in blocks:
        if b["tag"] == "p":
            parts.append(paragraph_block(b["text"]))
        else:
            level = int(b["tag"][1])
            parts.append(heading_block(b["text"], level))
    return "\n\n".join(parts)


PAGES = [
    {
        "slug": "home",
        "title": "Home",
        "meta_description": "Software GovTech para el control de la inversión pública: supervisión de obras y contratos, trazabilidad y datos para decidir mejor.",
        "blocks": [
            {"tag": "h1", "text": "Claridad total sobre cada peso público"},
            {"tag": "p", "text": "La plataforma que le da visibilidad total a la inversión del Estado. Once años monitoreando proyectos y contratos, ahora con inteligencia artificial."},
            {"tag": "h2", "text": "¿Qué es Interkont?"},
            {"tag": "p", "text": "Interkont es el brazo tecnológico para la transparencia del sector público. Combinamos tecnología, analítica de datos e inteligencia artificial con un equipo altamente cualificado, para que las entidades del Estado monitoreen su inversión y sus proyectos con total claridad."},
            {"tag": "p", "text": "Nuestra innovación y efectividad al servicio de la transparencia, avaladas por instituciones dentro y fuera del país."},
            {"tag": "p", "text": "Soluciones tecnológicas de alto valor agregado, especializadas en el seguimiento masivo y transparente de proyectos y contratos de alto impacto."},
            {"tag": "h2", "text": "Misión y visión"},
            {"tag": "h2", "text": "Nuestros productos"},
            {"tag": "p", "text": "Tres plataformas que llevan claridad e inteligencia a la gestión pública: vigilar la inversión, canalizar la ayuda social y automatizar con IA."},
            {"tag": "h2", "text": "Cotice en el Catálogo IAD"},
            {"tag": "p", "text": "Adquiera las soluciones de Interkont a través del Instrumento de Agregación de Demanda, directo desde la Tienda Virtual del Estado, sin un proceso licitatorio largo."},
            {"tag": "h3", "text": "¿Es una entidad estatal?"},
            {"tag": "p", "text": "Cotice hoy mismo en la Tienda Virtual del Estado Colombiano."},
            {"tag": "h2", "text": "Lo público, con evidencia"},
            {"tag": "p", "text": "De la mayor emergencia natural del país a la gestión cultural: tecnología que sostiene la operación cuando más importa."},
            {"tag": "h2", "text": "Vea su inversión con claridad total"},
            {"tag": "p", "text": "Solicite una demo de COBRA o cotice nuestras soluciones de IA. Le respondemos en menos de 24 horas."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "cobra",
        "title": "COBRA",
        "meta_description": "COBRA centraliza la supervisión de obras y contratos públicos: avance, presupuesto, evidencia en campo y alertas en un solo lugar.",
        "blocks": [
            {"tag": "h1", "text": "COBRA — revolucionando el control de obras y contratos"},
            {"tag": "p", "text": "La nueva manera de monitorear contratos, proyectos y obras. En cualquier momento y lugar, con control visual y en tiempo real."},
            {"tag": "h2", "text": "Todos los actores, una sola verdad"},
            {"tag": "p", "text": "COBRA permite el control de proyectos y contratos involucrando a todos los actores —contratistas, interventores, supervisores y partes interesadas— con información en tiempo real que le permite a la alta gerencia tomar las mejores decisiones."},
            {"tag": "p", "text": "Una combinación única de tecnología, analítica de datos, hardware y un equipo humano altamente cualificado, para que sus proyectos se ejecuten con total claridad."},
            {"tag": "h2", "text": "Capacidades que facilitan la gestión"},
            {"tag": "p", "text": "La última tecnología en cada componente para el control en tiempo real de proyectos y contratos."},
            {"tag": "h3", "text": "Eye Control"},
            {"tag": "p", "text": "Reconocimiento visual de fotos y videos con IA para identificar patrones. Su organización reconoce objetos en las imágenes registradas por los interventores y genera analíticas de datos masivas."},
            {"tag": "h2", "text": "Administre sus proyectos en tiempo real"},
            {"tag": "p", "text": "Involucramos toda la dinámica real entre contratistas, interventores y supervisores en una navegación fácil e intuitiva. Información de la mejor calidad, siempre a la mano, para lograr sus objetivos."},
            {"tag": "h2", "text": "Revolucione el control de sus obras con COBRA"},
            {"tag": "p", "text": "Conózcanos y vea cómo COBRA le da visibilidad total de proyectos y contratos en tiempo real."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "panal",
        "title": "PANAL",
        "meta_description": "PANAL organiza la ayuda social: focalización, entrega y seguimiento de beneficiarios con trazabilidad de punta a punta.",
        "blocks": [
            {"tag": "h1", "text": "PANAL — simplificamos la manera de ayudar"},
            {"tag": "p", "text": "Plataforma de asistencia a necesidades de ayudas localizadas: canalice con rapidez, eficiencia y transparencia todas las ayudas que una población pueda necesitar."},
            {"tag": "h2", "text": "Simplificamos la manera de ayudar"},
            {"tag": "p", "text": "Es una plataforma 100% web y móvil de última tecnología que permite canalizar con rapidez, eficiencia y transparencia todas las ayudas que una población pueda necesitar."},
            {"tag": "p", "text": "Gracias a nuestra gestión hemos logrado canalizar con éxito ayudas para más de 100.000 familias y 300.000 personas, haciendo seguimiento al proceso desde que se solicita la ayuda hasta que esta se convierte en realidad."},
            {"tag": "h2", "text": "Decisiones acertadas, respaldadas por datos"},
            {"tag": "p", "text": "Haciendo uso de inteligencia artificial y cruce con múltiples fuentes de datos logramos organizar toda la información relacionada a familias, grupos poblacionales y viviendas, de tal manera que se tomen las decisiones más acertadas para la asignación de ayudas y beneficios."},
            {"tag": "h2", "text": "Un registro guiado, validado en tiempo real"},
            {"tag": "p", "text": "La plataforma cuenta con formularios en línea en forma de wizard (paso a paso) que le permiten a un postulante registrar su caso. En tiempo real sus datos son cruzados con otras fuentes de información para validarlos y definir si es susceptible de ser beneficiario."},
            {"tag": "h2", "text": "Del registro a la entrega"},
            {"tag": "p", "text": "Cuatro etapas que aseguran que las ayudas lleguen a quienes más lo necesitan."},
            {"tag": "h2", "text": "Lleve la ayuda a quien más la necesita"},
            {"tag": "p", "text": "Conózcanos y descubra cómo canalizar ayudas con trazabilidad total."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "ik-labs",
        "title": "IK Labs",
        "meta_description": "IK Labs construye software a la medida, agentes de IA y productos de datos para operar mejor lo público.",
        "blocks": [
            {"tag": "h1", "text": "IK Labs — software, agentes y datos para operar mejor"},
            {"tag": "p", "text": "No somos una fábrica tradicional de software: somos agentic AI-first. Diseñamos, construimos e implementamos software empresarial, agentes inteligentes y soluciones de datos conversacionales."},
            {"tag": "h2", "text": "Somos agentic AI-first"},
            {"tag": "p", "text": "Combinamos desarrollo acelerado, automatización, inteligencia artificial, arquitectura de datos y conocimiento de negocio para entregar soluciones funcionales, medibles y sostenibles. Convertimos procesos complejos en capacidades digitales reales."},
            {"tag": "p", "text": "Construimos tecnología inteligente para que las organizaciones operen mejor, decidan más rápido y reduzcan la carga manual."},
            {"tag": "h2", "text": "AI Software Factory"},
            {"tag": "p", "text": "Desarrollamos tecnología en menos tiempo — sin depender de ciclos largos de desarrollo tradicional."},
            {"tag": "h2", "text": "IK Agent Suite"},
            {"tag": "p", "text": "No son chatbots genéricos. Cada agente consulta información, responde, genera reportes, ejecuta flujos, escala a humanos y deja trazabilidad de su operación."},
            {"tag": "h2", "text": "Solo pregunta. El agente responde."},
            {"tag": "p", "text": "No más buscar entre reportes dispersos. El usuario pregunta y el agente responde desde las fuentes conectadas: en texto, tablas, resúmenes, visualizaciones, alertas o reportes ejecutivos."},
            {"tag": "h3", "text": "Fuentes que conecta"},
            {"tag": "h2", "text": "Modelo comercial de agentes"},
            {"tag": "p", "text": "Tres etapas claras, del arranque a la evolución continua."},
            {"tag": "h2", "text": "Flexible y escalable"},
            {"tag": "p", "text": "Tu inversión combina un arranque por proyecto con un acompañamiento mensual — valor inmediato y evolución continua."},
            {"tag": "h2", "text": "Construyamos tecnología inteligente"},
            {"tag": "p", "text": "Hablemos de su reto y diseñemos el agente o la solución que su organización necesita."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "productos",
        "title": "Nuestros productos",
        "meta_description": "Toda la familia de productos Interkont en un solo lugar: COBRA, PANAL, IK Labs y el catálogo IAD.",
        "blocks": [
            {"tag": "h1", "text": "Toda la familia COBRA en un solo lugar"},
            {"tag": "p", "text": "Del despliegue en la nube a la inteligencia artificial: conozca cada producto y servicio de Interkont para el control y monitoreo de proyectos, contratos y obras del sector público."},
            {"tag": "h2", "text": "Elija el producto"},
            {"tag": "p", "text": "Nueve soluciones que cubren todo el ciclo: desde la plataforma en la nube hasta la analítica con IA, el soporte y la gobernanza de usuarios."},
            {"tag": "h3", "text": "COBRA Cloud"},
            {"tag": "p", "text": "Versión de entrada de la plataforma COBRA, lista para operar desde el momento en que se activa la licencia gracias a sus características preconfiguradas."},
            {"tag": "h3", "text": "COBRA Corporate"},
            {"tag": "p", "text": "Solución robusta para la gestión integral de proyectos y contratos, disponible en tres modelos de licenciamiento."},
            {"tag": "h3", "text": "COBRA Housing"},
            {"tag": "p", "text": "Versión especializada de COBRA para la gestión de proyectos de mejoramiento de vivienda —construcción, adecuación y mejora—, disponible en dos modalidades."},
            {"tag": "h3", "text": "Niveles de Implementación"},
            {"tag": "p", "text": "Cinco niveles escalables, aplicables a COBRA Corporate, COBRA Housing, COBRA BPM y el servicio SaaS de IA. Elija según el alcance y la madurez de su entidad."},
            {"tag": "h3", "text": "Servicio de Soporte"},
            {"tag": "p", "text": "Tres niveles de soporte, limitados por el número de usuarios, proyectos y contratos de la licencia. Disponible tanto en modalidad SaaS como On-Premise."},
            {"tag": "h3", "text": "COBRA BPM"},
            {"tag": "p", "text": "Módulo SaaS que añade a COBRA Corporate la capacidad de automatizar procesos y flujos de trabajo empresariales (BPM): desde procesos precontractuales hasta cualquier flujo que la organización necesite, con acceso remoto y en tiempo real, sin invertir en infraestructura adicional."},
            {"tag": "h3", "text": "Inteligencia Artificial"},
            {"tag": "p", "text": "DataWiz AI es una solución conversacional empresarial con IA generativa que conecta de forma segura los datos estructurados y no estructurados de la organización con modelos avanzados de lenguaje natural. Resuelve la dependencia de equipos técnicos, la información fragmentada y las decisiones basadas en la intuición."},
            {"tag": "h3", "text": "Otros Servicios y Módulos"},
            {"tag": "p", "text": "Módulos y servicios que amplían COBRA y PANAL para adaptarse a cada operación, del campo a la sala de decisiones."},
            {"tag": "h3", "text": "Política de Usuarios"},
            {"tag": "p", "text": "La Política de Gestión de Usuarios hace parte del Contrato de Licencia de Uso con Interkont S.A.S. y define el uso correcto de cada usuario nominal de la plataforma."},
            {"tag": "h2", "text": "¿No sabe qué producto necesita?"},
            {"tag": "p", "text": "Cuéntenos su reto y le ayudamos a elegir la combinación de productos y nivel de implementación ideal para su entidad."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "nosotros",
        "title": "Nosotros",
        "meta_description": "Somos amantes de la tecnología enfocada en la transparencia. Más de once años apoyando el control de lo público.",
        "blocks": [
            {"tag": "h1", "text": "Amantes de la tecnología enfocada en la transparencia"},
            {"tag": "p", "text": "Desarrollamos soluciones tecnológicas de alto valor agregado. Once años de experiencia focalizada en proyectos de alto impacto nos han valido casos de éxito tangibles y reconocimiento nacional e internacional."},
            {"tag": "h2", "text": "Una empresa global de software"},
            {"tag": "p", "text": "Interkont proporciona productos de software para todas las áreas de un negocio. Desarrollamos suites integrales por industria en la nube e implementamos tecnología de forma eficiente que prioriza la experiencia del usuario, aprovecha la ciencia de datos y se integra fácilmente en los sistemas existentes."},
            {"tag": "p", "text": "Más de 50.000 proyectos de nuestros clientes confían en Interkont para ayudar a superar las disrupciones del proceso de control y monitoreo."},
            {"tag": "h2", "text": "Un equipo que fija el estándar"},
            {"tag": "p", "text": "El multidisciplinario equipo directivo de Interkont establece el estándar para los más de 20 colaboradores en todo el mundo, demostrando cómo la transparencia, la colaboración y la responsabilidad fomentan mejores resultados empresariales."},
            {"tag": "p", "text": "Impulsamos el progreso continuo a través de la pasión y la resolución de problemas."},
            {"tag": "h2", "text": "Once años de impacto medible"},
            {"tag": "h3", "text": "Alejandro Gutiérrez"},
            {"tag": "p", "text": "Somos INTERKONT, y nos gusta definirnos como una fábrica de ideas: continuamente desarrollamos nuestra capacidad para convertir ideas en realidad. Creemos que todo desarrollo es posible — no nos limitamos, no nos intimidamos y empujamos al límite nuestras capacidades."},
            {"tag": "p", "text": "Premiamos y valoramos la excelencia y el dar siempre esa milla extra. Prestamos especial atención en lograr que nuestros productos tengan el “Efecto Wow”: estéticos, funcionales y que siempre entreguen algo más."},
            {"tag": "h2", "text": "Convirtamos su próxima idea en realidad"},
            {"tag": "p", "text": "Descubra cómo la tecnología de Interkont lleva claridad y transparencia a la gestión pública."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "blog",
        "title": "Blog",
        "meta_description": "Artículos de Interkont sobre gestión pública, tecnología, datos y transparencia.",
        "blocks": [
            {"tag": "h1", "text": "Ideas sobre lo público, la tecnología y los datos"},
            {"tag": "p", "text": "Análisis, casos de éxito y buenas prácticas sobre monitoreo de inversión pública, inteligencia artificial y transparencia, escritos por el equipo de Interkont."},
            {"tag": "h3", "text": "Reciba nuestros análisis"},
            {"tag": "p", "text": "Un correo al mes con lo que estamos aprendiendo sobre transparencia, datos e inversión pública. Sin ruido."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
    {
        "slug": "articulo",
        "title": "Once años monitoreando lo público: lo que aprendimos sobre la inversión del Estado",
        "meta_description": "Artículos de Interkont sobre gestión pública, tecnología, datos y transparencia.",
        "type": "post",
        "blocks": [
            {"tag": "h1", "text": "Once años monitoreando lo público: lo que aprendimos sobre la inversión del Estado"},
            {"tag": "p", "text": "Más de 50.000 proyectos y 6.500 millones de dólares supervisados nos dejaron una conclusión incómoda: el problema rara vez es la falta de datos, es la falta de visibilidad sobre ellos."},
            {"tag": "h2", "text": "El dato existe, la visibilidad no"},
            {"tag": "p", "text": "Cuando una entidad pública nos abre sus sistemas por primera vez, casi nunca encontramos un vacío de información. Encontramos lo contrario: hojas de cálculo, actas en PDF, correos con soportes, informes de interventoría, registros en SECOP. El dato está. Lo que no está es la capacidad de mirarlo todo junto y sacar una conclusión el mismo día."},
            {"tag": "p", "text": "Esa distancia entre <b>tener datos</b> y <b>tener visibilidad</b> es donde se pierden los proyectos. Un retraso que un supervisor detecta en campo tarda semanas en llegar a quien puede tomar la decisión de corregirlo. Para entonces, el sobrecosto ya está causado."},
            {"tag": "p", "text": "El problema del control público no es la ausencia de información. Es que la información llega tarde y fragmentada a quien decide."},
            {"tag": "h2", "text": "Tres patrones que se repiten"},
            {"tag": "h3", "text": "1. La información vive en silos"},
            {"tag": "p", "text": "Contratación tiene sus datos, financiera los suyos, la interventoría reporta por otro canal. Nadie está mintiendo; simplemente nadie ve el conjunto. La consolidación manual consume el tiempo que debería dedicarse al análisis."},
            {"tag": "h3", "text": "2. El reporte reemplaza al control"},
            {"tag": "p", "text": "Muchas entidades confunden reportar con controlar. Producir un informe mensual da la sensación de vigilancia, pero un informe describe el pasado. El control real exige alertas en el momento en que la desviación ocurre, no treinta días después."},
            {"tag": "h3", "text": "3. La evidencia no es verificable"},
            {"tag": "p", "text": "Una fotografía sin fecha, sin coordenadas y sin responsable no es evidencia: es una imagen. La trazabilidad exige que cada avance reportado tenga soporte comprobable."},
            {"tag": "h2", "text": "Qué cambia cuando hay visibilidad"},
            {"tag": "h2", "text": "Lo que sigue"},
            {"tag": "p", "text": "La siguiente frontera no es registrar mejor: es anticipar. Con analítica e inteligencia artificial es posible identificar qué proyectos tienen mayor probabilidad de retrasarse antes de que el retraso se materialice. Ese es el trabajo que hoy nos ocupa en IK Labs."},
        ],
    },
    {
        "slug": "catalogo-iad",
        "title": "Catálogo IAD",
        "meta_description": "Catálogo IAD de Interkont: soluciones disponibles para entidades públicas.",
        "blocks": [
            {"tag": "h1", "text": "Esta sección está en obra"},
            {"tag": "p", "text": "Estamos preparando el contenido del <b>Catálogo IAD</b> para que pueda cotizar nuestras soluciones directamente desde la Tienda Virtual del Estado Colombiano. Muy pronto disponible."},
            {"tag": "p", "text": "El brazo tecnológico profesional, creativo e innovador para la transparencia del sector público."},
        ],
    },
]


def create_page(page):
    kind = page.get("type", "page")
    endpoint = "posts" if kind == "post" else "pages"

    body = json.dumps({
        "title": page["title"],
        "slug": page["slug"],
        "status": "draft",
        "content": blocks_to_content(page["blocks"]),
        "excerpt": page["meta_description"],
    }).encode("utf8")

    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/{endpoint}",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    import base64
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"OK  [{kind:4s}] {page['slug']:16s} -> id={data['id']}  {data['link']}")
    except urllib.error.HTTPError as e:
        print(f"ERROR [{kind:4s}] {page['slug']:16s} -> HTTP {e.code}: {e.read().decode()[:300]}")


if __name__ == "__main__":
    for page in PAGES:
        create_page(page)
