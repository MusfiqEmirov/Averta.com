import html as html_lib
import re

from django import template
from django.utils.html import strip_tags

register = template.Library()


def _plain_text(value):
    if value is None:
        return ''
    raw = str(value)
    raw = re.sub(r'<\s*br\s*/?\s*>', ' ', raw, flags=re.I)
    raw = re.sub(r'</\s*(p|div|li|h[1-6]|blockquote|tr|td|th)\s*>', ' ', raw, flags=re.I)
    text = strip_tags(raw)
    text = html_lib.unescape(text)
    text = text.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', text).strip()


@register.filter
def plain_text(value):
    return _plain_text(value)


@register.inclusion_tag('partials/seo_meta.html', takes_context=True)
def seo_meta(
    context,
    description='',
    title='',
    og_type='website',
    image='',
    schema_type='organization',
    article_headline='',
    article_date='',
):
    og_image = image or context.get('og_image') or context.get('default_og_image')
    page_title = title or (article_headline if schema_type == 'article' and article_headline else '')
    return {
        'page_title': page_title,
        'seo_description': description,
        'og_type': og_type,
        'og_image': og_image,
        'canonical_url': context['canonical_url'],
        'site_url': context['site_url'],
        'site_name': context['site_name'],
        'seo_logo_url': context['seo_logo_url'],
        'language': context.get('language', 'az'),
        'schema_type': schema_type,
        'article_headline': article_headline,
        'article_date': article_date,
    }
