<?php
/**
 * Plugin Name: Interkont — Endpoint de formulario de contacto
 * Description: Expone POST /wp-json/interkont/v1/contacto para el formulario de
 *              contacto de interkont.co (sitio Astro, dominio distinto). Guarda cada
 *              solicitud como respaldo en Contacto -> Mensajes y la envía por correo
 *              (plantilla HTML + PDF adjunto) al equipo comercial.
 * Version: 2.0
 */

if (!defined('ABSPATH')) {
    exit;
}

// Destinatarios fijos (el servidor ignora el campo "to" que mande el navegador).
define('INTERKONT_CONTACT_EMAIL', 'german.zaldua@interkont.co,andres.lopez@interkont.co,alejandro.gutierrez@interkont.co');

// Orígenes del sitio público a los que se les permite llamar este endpoint (CORS).
define('INTERKONT_CONTACT_ALLOWED_ORIGINS', 'https://interkont.co,https://www.interkont.co');

// Máximo de solicitudes por IP y hora.
define('INTERKONT_CONTACT_RATE_LIMIT', 5);

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
        'ik_ref' => 'Ref.',
        'ik_nombre' => 'Nombre',
        'ik_correo' => 'Correo',
        'ik_telefono' => 'Teléfono',
        'ik_entidad' => 'Entidad',
        'ik_tema' => 'Tema',
        'ik_mensaje' => 'Mensaje',
        'ik_correo_enviado' => 'Correo enviado',
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

// CORS: refleja el origen solo si está en la lista permitida.
add_action('rest_api_init', function () {
    add_filter('rest_pre_serve_request', function ($served, $result, $request) {
        if (strpos($request->get_route(), '/interkont/v1/contacto') !== false) {
            $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
            $allowed = array_map('trim', explode(',', INTERKONT_CONTACT_ALLOWED_ORIGINS));
            if ($origin && in_array($origin, $allowed, true)) {
                header('Access-Control-Allow-Origin: ' . $origin);
                header('Vary: Origin');
            }
            header('Access-Control-Allow-Methods: POST, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type, Accept');
        }
        return $served;
    }, 10, 3);
});

function interkont_contact_error($status, $message)
{
    return new WP_REST_Response(['ok' => false, 'error' => $message], $status);
}

function interkont_contact_interest_label($code, $lang)
{
    $labels = [
        'cobra' => ['es' => 'COBRA · Control de obras y contratos', 'en' => 'COBRA · Works and contract control'],
        'panal' => ['es' => 'PANAL · Ayudas sociales', 'en' => 'PANAL · Social aid'],
        'iklabs' => ['es' => 'IK Labs · IA y software a la medida', 'en' => 'IK Labs · Custom AI and software'],
        'other' => ['es' => 'Otro', 'en' => 'Other'],
    ];
    return $labels[$code][$lang === 'en' ? 'en' : 'es'] ?? '';
}

function interkont_handle_contact_submission(WP_REST_Request $request)
{
    // Límite por IP: 5 solicitudes por hora.
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $rate_key = 'ik_contact_rl_' . md5($ip);
    $count = (int) get_transient($rate_key);
    if ($count >= INTERKONT_CONTACT_RATE_LIMIT) {
        return interkont_contact_error(429, 'Demasiadas solicitudes. Intente de nuevo más tarde.');
    }

    // Acepta multipart/form-data (formulario nuevo) o JSON (formulario de /contacto).
    $json = $request->get_json_params();
    $body = is_array($json) ? $json : $request->get_body_params();

    // Honeypot del formulario antiguo.
    if (!empty($body['sitio_web'])) {
        return new WP_REST_Response(['ok' => true], 200);
    }

    $legacy = isset($body['nombre']) || isset($body['correo']);
    $pick = function ($new, $old) use ($body) {
        return $body[$new] ?? ($body[$old] ?? '');
    };

    $name = sanitize_text_field($pick('name', 'nombre'));
    $email = sanitize_email($pick('email', 'correo'));
    $organization = sanitize_text_field($pick('organization', 'entidad'));
    $message = sanitize_textarea_field($pick('message', 'mensaje'));
    $lang = (($body['lang'] ?? 'es') === 'en') ? 'en' : 'es';
    $page = esc_url_raw($body['page'] ?? 'https://interkont.co/');

    $phone_raw = $pick('phone', 'telefono');
    $phone = preg_replace('/\D+/', '', (string) $phone_raw);
    $cc = preg_replace('/\D+/', '', (string) ($body['phone_country_code'] ?? ''));
    $phone_display = trim(($cc ? '+' . $cc . ' ' : '') . ($cc && strpos($phone, $cc) === 0 ? substr($phone, strlen($cc)) : $phone));
    if (!$cc && $phone) {
        $phone_display = '+' . $phone;
    }

    $interest = sanitize_text_field($body['interest'] ?? '');
    if ($legacy) {
        $interest_label = sanitize_text_field($body['tema'] ?? '');
    } else {
        $interest_label = interkont_contact_interest_label($interest, $lang);
    }

    // Validación (el servidor nunca confía solo en el navegador).
    if (mb_strlen($name) < 2 || !is_email($email) || !$message) {
        return interkont_contact_error(422, 'Faltan campos obligatorios o el correo no es válido.');
    }
    if (!$legacy) {
        $national = $cc && strpos($phone, $cc) === 0 ? substr($phone, strlen($cc)) : $phone;
        if (mb_strlen($organization) < 2 || strlen($national) < 7 || strlen($national) > 12 || !$interest_label) {
            return interkont_contact_error(422, 'Faltan campos obligatorios o tienen un formato no válido.');
        }
    }

    // Referencia única IK-AAMMDD-XXXX (se regenera si el cliente manda una inválida).
    $ref = sanitize_text_field($body['ref'] ?? '');
    if (!preg_match('/^IK-\d{6}-[A-Z0-9]{4}$/', $ref)) {
        $ref = 'IK-' . wp_date('ymd') . '-' . strtoupper(substr(wp_generate_password(8, false, false), 0, 4));
    }

    set_transient($rate_key, $count + 1, HOUR_IN_SECONDS);

    // Adjunto PDF (opcional): máximo 2 MB y firma %PDF.
    $attachments = [];
    $tmp_pdf = '';
    $files = $request->get_file_params();
    if (!empty($files['pdf']['tmp_name']) && is_uploaded_file($files['pdf']['tmp_name'])) {
        $size = (int) ($files['pdf']['size'] ?? 0);
        $head = file_get_contents($files['pdf']['tmp_name'], false, null, 0, 5);
        if ($size > 0 && $size <= 2 * 1024 * 1024 && $head === '%PDF-') {
            $tmp_pdf = trailingslashit(get_temp_dir()) . 'Solicitud-Interkont-' . $ref . '.pdf';
            if (copy($files['pdf']['tmp_name'], $tmp_pdf)) {
                $attachments[] = $tmp_pdf;
            }
        }
    }

    $post_id = wp_insert_post([
        'post_type' => 'ik_contact_msg',
        'post_status' => 'publish',
        'post_title' => sprintf('%s — %s', $name, current_time('Y-m-d H:i')),
    ]);

    if ($post_id && !is_wp_error($post_id)) {
        update_post_meta($post_id, 'ref', $ref);
        update_post_meta($post_id, 'nombre', $name);
        update_post_meta($post_id, 'correo', $email);
        update_post_meta($post_id, 'telefono', $phone_display ?: $phone);
        update_post_meta($post_id, 'entidad', $organization);
        update_post_meta($post_id, 'tema', $interest_label);
        update_post_meta($post_id, 'mensaje', $message);
    }

    $submitted_at = wp_date('d/m/Y H:i', null, new DateTimeZone('America/Bogota')) . ' (hora Colombia)';
    $html = interkont_contact_render_email([
        'ref' => $ref,
        'name' => $name,
        'organization' => $organization ?: '—',
        'email' => $email,
        'phone' => $phone ?: '57',
        'phone_display' => $phone_display ?: '—',
        'interest_label' => $interest_label ?: '—',
        'message' => $message,
        'submitted_at' => $submitted_at,
        'page' => $page ?: 'https://interkont.co/',
    ]);

    $subject = sprintf('Nueva solicitud de contacto · %s', $ref);
    $headers = [
        'Content-Type: text/html; charset=UTF-8',
        'Reply-To: ' . $name . ' <' . $email . '>',
    ];

    $sent = wp_mail(array_map('trim', explode(',', INTERKONT_CONTACT_EMAIL)), $subject, $html, $headers, $attachments);

    if ($tmp_pdf && file_exists($tmp_pdf)) {
        @unlink($tmp_pdf);
    }

    if ($post_id && !is_wp_error($post_id)) {
        update_post_meta($post_id, 'correo_enviado', $sent ? 'Sí' : 'No');
    }

    if (!$sent) {
        error_log("Interkont contacto: wp_mail() falló para la solicitud {$ref} (post #{$post_id})");
        return interkont_contact_error(500, 'No se pudo enviar el correo.');
    }

    return new WP_REST_Response(['ok' => true, 'ref' => $ref], 200);
}

// Reemplaza {{campo}} en la plantilla con los valores escapados.
function interkont_contact_render_email(array $vars)
{
    $html = interkont_contact_email_template();
    foreach ($vars as $key => $value) {
        $html = str_replace('{{' . $key . '}}', esc_html($value), $html);
    }
    return $html;
}

function interkont_contact_email_template()
{
    return <<<'NOWDOC_END'
<!DOCTYPE html>
<html lang="es" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>Nueva solicitud de contacto · {{ref}}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<style>
  @media only screen and (max-width:620px){
    .wrap{width:100% !important}
    .px{padding-left:20px !important; padding-right:20px !important}
    .ttl{font-size:28px !important; line-height:32px !important}
  }
  @media (prefers-color-scheme:dark){
    .bg-page{background-color:#17151D !important}
    .card{background-color:#221F2A !important}
    .t-main{color:#F4F3F5 !important}
    .t-soft{color:#B9B6C2 !important}
    .line{border-color:#3A3643 !important}
    .tile{background-color:#2C2833 !important}
  }
</style>
</head>
<body class="bg-page" style="margin:0;padding:0;background-color:#EFEEF2;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">

<span style="display:none !important;visibility:hidden;opacity:0;color:transparent;height:0;width:0;max-height:0;overflow:hidden;mso-hide:all;">{{name}} · {{organization}} quiere hablar de {{interest_label}}. Responda en menos de 24 horas.&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;</span>

<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" class="bg-page" bgcolor="#EFEEF2" style="background-color:#EFEEF2;">
<tr><td align="center" style="padding:28px 12px 36px;">

  <!--[if mso]><table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" align="center"><tr><td><![endif]-->
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" class="wrap" style="width:600px;max-width:600px;">

    <!-- Cabecera -->
    <tr><td class="px" bgcolor="#0B0910" style="background-color:#0B0910;border-radius:28px 28px 0 0;padding:34px 36px 30px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td style="font-family:Arial,Helvetica,sans-serif;font-size:22px;line-height:26px;font-weight:bold;letter-spacing:-0.5px;color:#FFFFFF;mso-line-height-rule:exactly;">interkont</td>
          <td align="right" style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#FF5C86;mso-line-height-rule:exactly;">Ref. {{ref}}</td>
        </tr>
      </table>
      <div style="font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:16px;font-weight:bold;letter-spacing:1.4px;text-transform:uppercase;color:#FF5C86;padding-top:34px;mso-line-height-rule:exactly;">Nueva solicitud de contacto</div>
      <div class="ttl" style="font-family:Arial,Helvetica,sans-serif;font-size:34px;line-height:38px;font-weight:bold;letter-spacing:-1px;color:#FFFFFF;padding-top:10px;mso-line-height-rule:exactly;">{{name}} quiere hablar con nosotros</div>
      <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:22px;color:#B9B6C2;padding-top:12px;mso-line-height-rule:exactly;">Recibida el {{submitted_at}} desde interkont.co</div>
    </td></tr>

    <!-- Barra de marca -->
    <tr><td height="6" bgcolor="#E70147" style="height:6px;line-height:6px;font-size:6px;background-color:#E70147;background-image:linear-gradient(108deg,#FFAA4A 0.5%,#E70147 99%);">&nbsp;</td></tr>

    <!-- Interés -->
    <tr><td class="card px" bgcolor="#FFFFFF" style="background-color:#FFFFFF;padding:26px 36px 8px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td bgcolor="#FCE7EF" style="background-color:#FCE7EF;border-radius:100px;padding:9px 16px;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:16px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:#EA215E;mso-line-height-rule:exactly;">Interés · {{interest_label}}</td>
      </tr></table>
    </td></tr>

    <!-- Datos -->
    <tr><td class="card px" bgcolor="#FFFFFF" style="background-color:#FFFFFF;padding:12px 36px 8px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" class="tile" bgcolor="#F4F3F5" style="background-color:#F4F3F5;border-radius:20px;">
            <tr><td style="padding:18px 28px;border-bottom:1px solid #E8E6EB;">
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#66646E;mso-line-height-rule:exactly;">Nombre completo</div>
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:24px;font-weight:bold;color:#131117;padding-top:4px;mso-line-height-rule:exactly;">{{name}}</div>
            </td></tr>
            <tr><td style="padding:18px 28px;border-bottom:1px solid #E8E6EB;">
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#66646E;mso-line-height-rule:exactly;">Correo institucional</div>
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:24px;font-weight:bold;color:#131117;padding-top:4px;mso-line-height-rule:exactly;"><a href="mailto:{{email}}" style="color:#EA215E;text-decoration:none;">{{email}}</a></div>
            </td></tr>
            <tr><td style="padding:18px 28px;border-bottom:1px solid #E8E6EB;">
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#66646E;mso-line-height-rule:exactly;">Celular</div>
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:24px;font-weight:bold;color:#131117;padding-top:4px;mso-line-height-rule:exactly;"><a href="tel:+{{phone}}" style="color:#131117;text-decoration:none;">{{phone_display}}</a></div>
            </td></tr>
            <tr><td style="padding:18px 28px;">
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#66646E;mso-line-height-rule:exactly;">Entidad o empresa</div>
              <div style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:24px;font-weight:bold;color:#131117;padding-top:4px;mso-line-height-rule:exactly;">{{organization}}</div>
            </td></tr>
      </table>
    </td></tr>

    <!-- Mensaje -->
    <tr><td class="card px" bgcolor="#FFFFFF" style="background-color:#FFFFFF;padding:16px 36px 8px;">
      <div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:14px;font-weight:bold;letter-spacing:1.2px;text-transform:uppercase;color:#66646E;padding:0 0 10px;mso-line-height-rule:exactly;" class="t-soft">Mensaje</div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td bgcolor="#FBFAFC" class="tile" style="background-color:#FBFAFC;border:1px solid #E8E6EB;border-radius:18px;padding:20px 22px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:26px;color:#131117;mso-line-height-rule:exactly;white-space:pre-wrap;">{{message}}</td>
      </tr></table>
    </td></tr>

    <!-- Acciones -->
    <tr><td class="card px" bgcolor="#FFFFFF" style="background-color:#FFFFFF;padding:24px 36px 8px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
        <td width="50%" valign="top" style="padding-right:6px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
                <td align="center" bgcolor="#E70147" style="border-radius:100px;background-image:linear-gradient(108deg,#FFAA4A 0.5%,#E70147 99%);">
                  <a href="mailto:{{email}}?subject=Re:%20Su%20solicitud%20en%20Interkont%20%C2%B7%20{{ref}}" target="_blank" style="font-family:Arial,Helvetica,sans-serif;display:block;padding:15px 24px;font-size:15px;line-height:20px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:100px;mso-line-height-rule:exactly;">Responder por correo</a>
                </td></tr></table></td>
        <td width="50%" valign="top" style="padding-left:6px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"><tr>
                <td align="center" bgcolor="#131117" style="border-radius:100px;">
                  <a href="https://wa.me/{{phone}}" target="_blank" style="font-family:Arial,Helvetica,sans-serif;display:block;padding:15px 24px;font-size:15px;line-height:20px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:100px;mso-line-height-rule:exactly;">Escribir por WhatsApp</a>
                </td></tr></table></td>
      </tr></table>
    </td></tr>

    <!-- Compromiso -->
    <tr><td class="card px" bgcolor="#FFFFFF" style="background-color:#FFFFFF;border-radius:0 0 28px 28px;padding:20px 36px 34px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" class="line" style="border-top:1px solid #E8E6EB;"><tr>
        <td style="padding-top:18px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:22px;color:#66646E;mso-line-height-rule:exactly;" class="t-soft"><strong style="color:#131117;" class="t-main">Responder en menos de 24 horas.</strong> El PDF de la solicitud va adjunto a este correo.</td>
      </tr></table>
    </td></tr>

    <!-- Pie -->
    <tr><td class="px" align="center" style="padding:22px 24px 0;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:19px;color:#66646E;mso-line-height-rule:exactly;">
      <span class="t-soft">Notificación automática generada por el formulario de <a href="{{page}}" style="color:#EA215E;text-decoration:none;">interkont.co</a>.<br>
      Los datos del solicitante son personales: trátelos según la Política de Tratamiento de Datos Personales de Interkont.<br>
      © 2026 Interkont · Powerful Technology</span>
    </td></tr>

  </table>
  <!--[if mso]></td></tr></table><![endif]-->

</td></tr>
</table>
</body>
</html>
NOWDOC_END;
}
