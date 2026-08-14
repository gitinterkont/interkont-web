<?php
/**
 * Plugin Name: Interkont — Menú principal (headless)
 * Description: Registra la ubicación de menú "Menú principal" para que
 *              WPGraphQL pueda exponerla al frontend de Astro. Sin esto,
 *              Apariencia -> Menús no tiene dónde asignar el menú y
 *              WPGraphQL no sabe qué ítems devolver.
 * Version: 1.0
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('after_setup_theme', function () {
    register_nav_menus([
        'primary' => __('Menú principal (sitio headless)'),
    ]);
});
