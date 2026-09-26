import logging

from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

from services.forms.forms_v1 import BookingForm
from services.models import Service
from services.utils.queries import get_background_image, get_contact, get_language_from_request, serialize_contact


def _absolute_uri(request, path):
    return request.build_absolute_uri(path)


def _resolve_default_og_image(request):
    og_rel = 'assets/img/averta-logo.webp'
    favicon_rel = 'assets/img/averta-favicon.webp'
    rel_path = og_rel if finders.find(og_rel) else favicon_rel
    return _absolute_uri(request, static(rel_path))


def seo(request):
    site_root = _absolute_uri(request, '/').rstrip('/')
    logo_path = static('assets/img/averta-logo.webp')
    if not finders.find('assets/img/averta-logo.webp'):
        logo_path = static('assets/img/averta-favicon.webp')

    return {
        'site_url': site_root,
        'site_name': 'Averta Travel',
        'canonical_url': _absolute_uri(request, request.path),
        'default_og_image': _resolve_default_og_image(request),
        'seo_logo_url': _absolute_uri(request, logo_path),
    }


def navbar_services(request):
    """Inject active services into every template for the navbar dropdown."""
    lang = (
        request.session.get('django_language')
        or request.session.get('language')
        or getattr(request, 'LANGUAGE_CODE', 'az')
    )
    if lang not in ('az', 'en', 'ru'):
        lang = 'az'

    name_field = f'name_{lang}'

    try:
        services = (
            Service.objects
            .filter(is_active=True)
            .only('slug', 'name_az', 'name_en', 'name_ru')
            .order_by('sort_order', 'id')
        )
        result = [
            {
                'slug': s.slug,
                'name': getattr(s, name_field, None) or s.name_az,
            }
            for s in services
        ]
    except Exception:
        result = []

    return {'navbar_services': result}


def _safe_bg(page_type):
    """Return background image URL or None — never raises."""
    try:
        return get_background_image(page_type)
    except Exception:
        return None


def site_contact(request):
    """Əlaqə məlumatları — footer, WhatsApp/zəng düymələri."""
    try:
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        contact_data = serialize_contact(contact, lang) if contact else None
    except Exception:
        contact_data = None

    return {
        'contact': contact_data,
        'home_contact_bg': _safe_bg('home_contact'),
    }


def turnstile(request):
    """Expose Cloudflare Turnstile keys to templates."""
    site_key = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
    secret_key = (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
    enabled = bool(site_key and secret_key)
    return {
        'turnstile_enabled': enabled,
        'turnstile_site_key': site_key,
    }


def modal_booking_form(request):
    """Global sifariş modalı üçün form."""
    lang = (
        request.session.get('django_language')
        or request.session.get('language')
        or getattr(request, 'LANGUAGE_CODE', 'az')
    )
    if lang not in ('az', 'en', 'ru'):
        lang = 'az'
    try:
        form = BookingForm(lang=lang, prefix='modal', initial={'booking_type': 'package'})
    except Exception:
        logging.getLogger(__name__).exception('modal_booking_form yaradıla bilmədi')
        try:
            form = BookingForm(lang='az', prefix='modal', initial={'booking_type': 'package'})
        except Exception:
            logging.getLogger(__name__).exception('modal_booking_form fallback da uğursuz oldu')
            form = None
    return {'modal_booking_form': form}
