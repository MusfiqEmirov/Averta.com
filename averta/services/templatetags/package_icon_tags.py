from django import template
from django.utils.safestring import mark_safe

from services.utils.package_icons import get_icon_svg_markup

register = template.Library()


@register.simple_tag
def package_icon_svg(icon_type, icon_variant='1', css_class='pkg-card__icon'):
    return mark_safe(get_icon_svg_markup(icon_type, icon_variant, css_class))
