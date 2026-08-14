<?php
/**
 * Plugin Name: Interkont — Endpoint de formulario de contacto
 * Description: Expone POST /wp-json/interkont/v1/contacto para que el
 *              formulario de contacto en interkont.co (sitio Astro,
 *              dominio distinto) pueda enviar mensajes. Guarda cada
 *              mensaje como respaldo en Contacto -> Mensajes y lo envía
 *              por correo a la dirección configurada abajo.
 * Version: 1.0
 */

if (!defined('ABSPATH')) {
    exit;
}

// Cambia esto si el correo de contacto es otro.
define('INTERKONT_CONTACT_EMAIL', 'contacto@interkont.co');

// Dominio del sitio público (Astro/Vercel) al que se le permite llamar
// este endpoint desde el navegador -- sin esto, el navegador bloquea la
// petición por CORS al ser un dominio distinto al de WordPress.
define('INTERKONT_CONTACT_ALLOWED_ORIGIN', 'https://interkont.co');

// --- Custom post type: respaldo de cada mensaje recibido ---

add_action('init', function () {
    register_post_type('ik_contact_msg', [
        'label' => 'Mensajes de contacto',
        'labels' => [
            'name' => 'Mensajes de contacto',
            'singular_name' => 'Mensaje de contacto',
            'menu_name' => 'Contacto',
            'all_items' => 'Todos los mensajes',
        ],
        'public' => false,
        'show_ui' => true,
        'show_in_menu' => true,
        'menu_icon' => 'dashicons-email-alt',
        'supports' => ['title'],
        'capability_type' => 'post',
        'map_meta_cap' => true,
    ]);
});

add_filter('manage_ik_contact_msg_posts_columns', function ($columns) {
    return [
        'cb' => $columns['cb'],
        'title' => 'Recibido',
        'ik_nombre' => 'Nombre',
        'ik_correo' => 'Correo',
        'ik_telefono' => 'Teléfono',
        'ik_tema' => 'Tema',
        'ik_mensaje' => 'Mensaje',
        'date' => 'Fecha',
    ];
});

add_action('manage_ik_contact_msg_posts_custom_column', function ($column, $post_id) {
    if (strpos($column, 'ik_') !== 0) {
        return;
    }
    $field = substr($column, 3);
    $value = get_post_meta($post_id, $field, true);
    echo esc_html($field === 'mensaje' ? wp_trim_words($value, 12) : $value);
}, 10, 2);

// --- Endpoint REST ---

add_action('rest_api_init', function () {
    register_rest_route('interkont/v1', '/contacto', [
        'methods' => 'POST',
        'callback' => 'interkont_handle_contact_submission',
        'permission_callback' => '__return_true',
    ]);
});

// Responde a las peticiones CORS preflight (OPTIONS) que el navegador
// manda antes del POST real cuando el origen es un dominio distinto.
add_action('rest_api_init', function () {
    add_filter('rest_pre_serve_request', function ($served, $result, $request) {
        if (strpos($request->get_route(), '/interkont/v1/contacto') !== false) {
            header('Access-Control-Allow-Origin: ' . INTERKONT_CONTACT_ALLOWED_ORIGIN);
            header('Access-Control-Allow-Methods: POST, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type');
        }
        return $served;
    }, 10, 3);
});

function interkont_handle_contact_submission(WP_REST_Request $request)
{
    $body = $request->get_json_params() ?? [];

    // Honeypot: campo oculto que un humano nunca llena, pero un bot
    // automático sí. Si viene con contenido, se descarta en silencio
    // como si hubiera funcionado, para no darle pistas al bot.
    if (!empty($body['sitio_web'])) {
        return new WP_REST_Response(['ok' => true], 200);
    }

    $nombre = sanitize_text_field($body['nombre'] ?? '');
    $correo = sanitize_email($body['correo'] ?? '');
    $telefono = sanitize_text_field($body['telefono'] ?? '');
    $entidad = sanitize_text_field($body['entidad'] ?? '');
    $tema = sanitize_text_field($body['tema'] ?? '');
    $mensaje = sanitize_textarea_field($body['mensaje'] ?? '');

    if (!$nombre || !$correo || !is_email($correo) || !$mensaje) {
        return new WP_REST_Response(
            ['ok' => false, 'error' => 'Faltan campos obligatorios o el correo no es válido.'],
            400
        );
    }

    $post_id = wp_insert_post([
        'post_type' => 'ik_contact_msg',
        'post_status' => 'publish',
        'post_title' => sprintf('%s — %s', $nombre, current_time('Y-m-d H:i')),
    ]);

    if ($post_id && !is_wp_error($post_id)) {
        update_post_meta($post_id, 'nombre', $nombre);
        update_post_meta($post_id, 'correo', $correo);
        update_post_meta($post_id, 'telefono', $telefono);
        update_post_meta($post_id, 'entidad', $entidad);
        update_post_meta($post_id, 'tema', $tema);
        update_post_meta($post_id, 'mensaje', $mensaje);
    }

    $subject = sprintf('Nuevo mensaje de contacto — %s', $nombre);
    $lines = [
        "Nombre: {$nombre}",
        "Correo: {$correo}",
        "Teléfono: " . ($telefono ?: '(no indicado)'),
        "Entidad: " . ($entidad ?: '(no indicada)'),
        "Tema de interés: " . ($tema ?: '(no indicado)'),
        '',
        'Mensaje:',
        $mensaje,
    ];
    $headers = ["Reply-To: {$nombre} <{$correo}>"];

    $sent = wp_mail(INTERKONT_CONTACT_EMAIL, $subject, implode("\n", $lines), $headers);

    if (!$sent) {
        error_log("Interkont contacto: wp_mail() falló para el mensaje de {$correo} (post #{$post_id})");
    }

    // Se responde "ok" aunque el correo falle: el mensaje ya quedó
    // guardado como respaldo en Contacto -> Mensajes, así que no se
    // pierde nada aunque el envío de correo no llegue.
    return new WP_REST_Response(['ok' => true], 200);
}
