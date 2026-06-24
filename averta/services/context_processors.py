import logging

from django.conf import settings

from services.forms.forms_v1 import BookingForm
from services.models import Service
from services.utils.queries import get_background_image, get_contact, get_language_from_request, serialize_contact


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
