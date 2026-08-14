<?php
/**
 * Plugin Name: Interkont — Deploy Hooks (Vercel + GitHub Pages)
 * Description: Dispara un rebuild cada vez que se publica o actualiza una
 *              página o un post: preview en Vercel y produccion
 *              (interkont.co) en GitHub Pages via repository_dispatch.
 *              El token de GitHub NO se define aqui -- agregalo en
 *              wp-config.php como GH_DISPATCH_TOKEN.
 * Version: 2.0
 */

if (!defined('ABSPATH')) {
    exit;
}

// Deploy Hook de Vercel (Settings -> Git -> Deploy Hooks).
define('VERCEL_DEPLOY_HOOK_URL', 'https://api.vercel.com/v1/integrations/deploy/prj_FNbqG5CGH7SvKocPz4ytSLw4NvNf/yrhmpNq4JA');

// Repo de GitHub cuyo workflow de Pages escucha repository_dispatch.
define('GH_DISPATCH_REPO', 'gitinterkont/interkont-web');

add_action('transition_post_status', function ($new_status, $old_status, $post) {
    // Solo paginas y posts, y solo cuando el resultado final es "publicado"
    // (cubre publicaciones nuevas y ediciones a contenido ya publicado).
    if (!in_array($post->post_type, ['post', 'page'], true)) {
        return;
    }
    if ($new_status !== 'publish') {
        return;
    }

    // 'blocking' => true a proposito en ambas llamadas: en varios hostings
    // compartidos una peticion no-bloqueante se corta antes de completarse
    // porque PHP termina de procesar la pagina antes de que la peticion
    // saliente realmente se envie. Cuesta un par de segundos extra al
    // guardar, pero asegura que el webhook llegue.

    if (defined('VERCEL_DEPLOY_HOOK_URL') && VERCEL_DEPLOY_HOOK_URL !== 'PASTE_URL_HERE') {
        $result = wp_remote_post(VERCEL_DEPLOY_HOOK_URL, [
            'timeout'  => 8,
            'blocking' => true,
        ]);
        if (is_wp_error($result)) {
            error_log('Vercel Deploy Hook error: ' . $result->get_error_message());
        } else {
            error_log('Vercel Deploy Hook: HTTP ' . wp_remote_retrieve_response_code($result));
        }
    }

    if (defined('GH_DISPATCH_TOKEN') && GH_DISPATCH_TOKEN !== '') {
        $result = wp_remote_post('https://api.github.com/repos/' . GH_DISPATCH_REPO . '/dispatches', [
            'timeout'  => 8,
            'blocking' => true,
            'headers'  => [
                'Authorization' => 'Bearer ' . GH_DISPATCH_TOKEN,
                'Accept'        => 'application/vnd.github+json',
                'User-Agent'    => 'interkont-wp-deploy-hook',
            ],
            'body' => wp_json_encode(['event_type' => 'wordpress-published']),
        ]);
        if (is_wp_error($result)) {
            error_log('GitHub Pages Dispatch error: ' . $result->get_error_message());
        } else {
            error_log('GitHub Pages Dispatch: HTTP ' . wp_remote_retrieve_response_code($result));
        }
    }
}, 10, 3);
