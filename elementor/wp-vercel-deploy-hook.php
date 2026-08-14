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
define('VERCEL_DEPLOY_HOOK_URL', 'PASTE_URL_HERE');

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

    wp_remote_post(VERCEL_DEPLOY_HOOK_URL, [
        'timeout'  => 5,
        'blocking' => false, // no hace esperar al editor mientras guarda
    ]);
}, 10, 3);
