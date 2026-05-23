from django.utils import translation
from django.conf import settings


class PublicHtmlCacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            return response
        content_type = (response.get('Content-Type') or '').split(';')[0].strip().lower()
        if content_type == 'text/html' and response.status_code == 200:
            if 'Cache-Control' not in response:
                response['Cache-Control'] = 'private, no-cache, must-revalidate'
            if 'Vary' not in response:
                response['Vary'] = 'Cookie, Accept-Language'
        return response


class CustomLocaleMiddleware:
    LANGUAGES = {
        'az': 'Azərbaycan',
        'en': 'English',
        'ru': 'Русский',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_prefix = f'/{settings.ADMIN_URL.strip("/")}'
        if request.path.startswith(admin_prefix):
            admin_lang = (
                request.session.get('admin_language')
                or getattr(settings, 'ADMIN_LANGUAGE_CODE', 'az')
            )
            if admin_lang not in self.LANGUAGES:
                admin_lang = getattr(settings, 'ADMIN_LANGUAGE_CODE', 'az')
            translation.activate(admin_lang)
            request.LANGUAGE_CODE = admin_lang
            return self.get_response(request)

        language = request.session.get('django_language') or request.session.get('language')
        if language and language in self.LANGUAGES:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            site_default = getattr(settings, 'LANGUAGE_CODE', 'az')
            if site_default not in self.LANGUAGES:
                site_default = 'az'
            translation.activate(site_default)
            request.LANGUAGE_CODE = site_default

        return self.get_response(request)
