from services.models import Service


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
            .order_by('name_az')
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
