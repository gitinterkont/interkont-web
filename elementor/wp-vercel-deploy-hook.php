<?php
/**
 * Plugin Name: Interkont — Vercel Deploy Hook
 * Description: Dispara un rebuild en Vercel cada vez que se publica o
 *              actualiza una página o un post. Reemplaza VERCEL_DEPLOY_HOOK_URL
 *              por la URL real antes de activar el plugin.
 * Version: 1.0
 */

if (!defined('ABSPATH')) {
    exit;
}

// Pega aqui la URL del Deploy Hook de Vercel (Settings -> Git -> Deploy Hooks).
define('VERCEL_DEPLOY_HOOK_URL', 'https://api.vercel.com/v1/integrations/deploy/prj_FNbqG5CGH7SvKocPz4ytSLw4NvNf/yrhmpNq4JA');

add_action('transition_post_status', function ($new_status, $old_status, $post) {
    // Solo paginas y posts, y solo cuando el resultado final es "publicado"
    // (cubre publicaciones nuevas y ediciones a contenido ya publicado).
    if (!in_array($post->post_type, ['post', 'page'], true)) {
        return;
    }
    if ($new_status !== 'publish') {
        return;
    }
    if (defined('VERCEL_DEPLOY_HOOK_URL') && VERCEL_DEPLOY_HOOK_URL === 'PASTE_URL_HERE') {
        return; // evita disparar con la URL de ejemplo sin configurar
    }

    // 'blocking' => true a proposito: en varios hostings compartidos una
    // peticion no-bloqueante se corta antes de completarse porque PHP
    // termina de procesar la pagina antes de que la peticion saliente
    // realmente se envie. Cuesta un par de segundos extra al guardar,
    // pero asegura que el webhook llegue.
    $result = wp_remote_post(VERCEL_DEPLOY_HOOK_URL, [
        'timeout'  => 8,
        'blocking' => true,
    ]);

    if (is_wp_error($result)) {
        error_log('Vercel Deploy Hook error: ' . $result->get_error_message());
    } else {
        error_log('Vercel Deploy Hook: HTTP ' . wp_remote_retrieve_response_code($result));
    }
}, 10, 3);
