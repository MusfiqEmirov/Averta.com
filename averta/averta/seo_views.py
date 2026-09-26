from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    domain = getattr(settings, 'SITE_DOMAIN', 'www.avertatravel.com')
    domain = domain.replace('https://', '').replace('http://', '').strip('/')
    sitemap_url = f'https://{domain}/sitemap.xml'
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Disallow: /{settings.ADMIN_URL.strip("/")}/',
        'Disallow: /i18n/',
        'Disallow: /blog/api/',
        '',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
