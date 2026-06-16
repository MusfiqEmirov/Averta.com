import html as html_lib
import re

from django.db.models import Q, Prefetch
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.template.defaultfilters import truncatewords_html
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from services.models.media_models import media_not_marked_as_background_q
from services.models import (
    Service, Package, Partner, About,
    Contact, Media, Motto, Statistic, Blog, FAQ, Review,
)
from services.utils.cache_utils import cached_query, get_query_cache_key, cached_page_data
from services.utils.package_icons import TYPE_HEADER_GRADIENTS
from django.core.cache import cache


# ---------------------------------------------------------------------------
# Language helpers
# ---------------------------------------------------------------------------

def get_language_from_request(request):
    lang = request.GET.get('lang', '').lower() or request.GET.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang

    lang = request.session.get('django_language', '').lower()
    if lang in ['az', 'en', 'ru']:
        translation.activate(lang)
        return lang

    lang = request.session.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang

    lang = getattr(request, 'LANGUAGE_CODE', 'az')
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang

    request.session['django_language'] = 'az'
    request.session['language'] = 'az'
    request.session.modified = True
    translation.activate('az')
    return 'az'


def get_localized_field_name(field_base, lang):
    if lang == 'en':
        return f'{field_base}_en'
    elif lang == 'ru':
        return f'{field_base}_ru'
    else:
        return f'{field_base}_az'


def _localized_with_az_fallback(instance, lang, base):
    primary = getattr(instance, get_localized_field_name(base, lang), None) or ''
    if str(primary).strip():
        return primary
    return getattr(instance, get_localized_field_name(base, 'az'), None) or ''


def prepare_rich_html(value):
    """CKEditor HTML — decode entities, normalize empty paragraphs."""
    if not value:
        return ''
    text = html_lib.unescape(str(value))
    if '&lt;' in text or '&amp;lt;' in text:
        text = html_lib.unescape(text)
    text = re.sub(r'<p>(\s|&nbsp;|<br\s*/?>)*</p>', '', text, flags=re.IGNORECASE)
    return text.strip()


def build_about_description_preview(html, word_count=45):
    """Ana səhifə üçün qısa HTML preview (bağlı teqlər saxlanır)."""
    html = prepare_rich_html(html)
    if not html:
        return ''
    html = re.sub(r'<(script|style|iframe)[^>]*>.*?</\1>', '', html, flags=re.IGNORECASE | re.DOTALL)
    return truncatewords_html(html, word_count)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

def service_content_media_queryset():
    return (
        Media.objects.filter(image__isnull=False)
        .filter(media_not_marked_as_background_q())
        .order_by('created_at', 'id')
    )


def get_services(lang='az', is_active=True, on_main_page=None):
    queryset = Service.objects.prefetch_related(
        Prefetch('medias', queryset=service_content_media_queryset())
    )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)

    return queryset.order_by('-created_at', '-id')


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_service_by_slug(slug, lang='az'):
    try:
        return Service.objects.prefetch_related(
            Prefetch('medias', queryset=service_content_media_queryset())
        ).get(slug=slug, is_active=True)
    except Service.DoesNotExist:
        return None


def get_other_services(exclude_slug, lang='az', limit=6):
    qs = (
        get_services(lang=lang, is_active=True)
        .exclude(slug=exclude_slug)
        .order_by('-created_at', '-id')[:limit]
    )
    return [serialize_service(s, lang) for s in qs]


# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

def _az_from_suffix_for_amount(amount):
    """Return «dan» or «dən» based on the last digit of the amount."""
    for ch in reversed(str(amount)):
        if ch.isdigit():
            if ch in '069':
                return 'dan'
            return 'dən'
    return 'dan'


def format_package_price(price, currency, price_from=False, lang='az'):
    if price is None:
        return None

    symbols = {
        Package.CURRENCY_AZN: '₼',
        Package.CURRENCY_USD: '$',
        Package.CURRENCY_EUR: '€',
    }
    symbol = symbols.get(currency, currency)
    if price == price.to_integral_value():
        amount = int(price)
    else:
        amount = price.normalize() if hasattr(price, 'normalize') else price

    if price_from and lang == 'az':
        suffix = _az_from_suffix_for_amount(amount)
        return f'{symbol}{amount}-{suffix}'

    if currency == Package.CURRENCY_AZN:
        base = f'{amount} {symbol}'
    else:
        base = f'{symbol}{amount}'

    if not price_from:
        return base

    if lang == 'ru':
        return f'от {base}'
    if lang == 'en':
        return f'from {base}'
    return base


def get_packages(lang='az', is_active=True):
    from django.utils import timezone

    queryset = Package.objects.prefetch_related('service')

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    today = timezone.now().date()
    queryset = queryset.filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )

    return queryset.order_by('-created_at')


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_about(lang='az'):
    return About.objects.prefetch_related(
        Prefetch(
            'medias',
            queryset=Media.objects.filter(
                image__isnull=False,
            ).filter(media_not_marked_as_background_q()).order_by('id'),
        )
    ).first()


# ---------------------------------------------------------------------------
# Partners
# ---------------------------------------------------------------------------

def get_partners(lang='az', is_active=True):
    queryset = Partner.objects.prefetch_related(
        Prefetch(
            'medias',
            queryset=Media.objects.filter(image__isnull=False).filter(
                media_not_marked_as_background_q(),
            ).order_by('id'),
        )
    )
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return queryset.order_by('-created_at')


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_contact(lang='az'):
    return Contact.objects.first()


# ---------------------------------------------------------------------------
# Background images
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_background_image(page_type):
    image_map = {
        'home': 'is_home_page_background_image',
        'about': 'is_about_page_background_image',
        'contact': 'is_contact_page_background_image',
        'service': 'is_service_page_background_image',
        'blog': 'is_blog_page_background_image',
        'home_contact': 'is_home_contact_background_image',
        'contact_booking': 'is_contact_booking_background_image',
    }

    if page_type not in image_map:
        return None

    # If multiple images are marked as background, prefer the newest one.
    media = (
        Media.objects
        .filter(**{image_map[page_type]: True}, image__isnull=False)
        .order_by('-created_at', '-id')
        .first()
    )
    if media and media.image:
        return media.image.url
    return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_home_background_images(limit=6):
    media_list = Media.objects.filter(
        is_home_page_background_image=True,
        image__isnull=False
    ).order_by('-created_at')[:limit]
    return [media.image.url for media in media_list if media.image]


# ---------------------------------------------------------------------------
# Motto / hero carousel
# ---------------------------------------------------------------------------

PAGE_MOTTO_FLAGS = {
    'about': 'is_about_page',
    'contact': 'is_contact_page',
    'service': 'is_service_page',
    'package': 'is_package_page',
    'blog': 'is_blog_page',
}


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_page_motto(page_key, lang='az'):
    flag = PAGE_MOTTO_FLAGS.get(page_key)
    if not flag:
        return None
    motto = Motto.objects.filter(**{flag: True}).order_by('id').first()
    if not motto:
        return None
    text_field = get_localized_field_name('text', lang)
    return getattr(motto, text_field, motto.text_az) or motto.text_az


def get_motto_texts(lang='az'):
    text_field = get_localized_field_name('text', lang)
    texts = []
    for m in Motto.objects.filter(show_on_home_hero=True).order_by('id'):
        text = (getattr(m, text_field, m.text_az) or m.text_az or '').strip()
        if text:
            texts.append(text)
    return texts


def build_hero_carousel(lang):
    """
    Hər slayd üçün fon şəkli + (varsa) öz devizi.
    Next/prev ilə növbəti slayda növbəti motto göstərilir.
    """
    motto_texts = get_motto_texts(lang)
    urls = list(get_home_background_images(limit=6))
    if not urls:
        return []

    n_images = len(urls)
    n_mottos = len(motto_texts)
    n_slides = max(n_images, n_mottos) if n_mottos else n_images

    slides = []
    for i in range(n_slides):
        slides.append({
            'image_url': urls[i % n_images],
            'motto': motto_texts[i] if i < n_mottos else None,
        })
    return slides


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def _stat_icon(value, default):
    from services.models.statistic_models import STAT_ICON_CHOICES

    allowed = {choice[0] for choice in STAT_ICON_CHOICES}
    if value in allowed:
        return value
    return default


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_statistics(lang='az'):
    from services.models.statistic_models import STAT_ICON_DEFAULTS

    statistic = Statistic.objects.first()
    if not statistic:
        return {}

    def caption(base):
        return (_localized_with_az_fallback(statistic, lang, base) or '').strip()

    card_defs = (
        (statistic.value_one, 'caption_one', statistic.icon_one, STAT_ICON_DEFAULTS[0], 1),
        (statistic.value_two, 'caption_two', statistic.icon_two, STAT_ICON_DEFAULTS[1], 2),
        (statistic.value_three, 'caption_three', statistic.icon_three, STAT_ICON_DEFAULTS[2], 3),
        (statistic.value_four, 'caption_four', statistic.icon_four, STAT_ICON_DEFAULTS[3], 4),
    )

    cards = []
    for value, caption_base, icon_val, default_icon, variant in card_defs:
        if value is None:
            continue
        cards.append({
            'value': value,
            'caption': caption(caption_base),
            'icon': _stat_icon(icon_val, default_icon),
            'variant': variant,
        })

    if not cards:
        return {}

    return {
        'value_one': statistic.value_one,
        'value_two': statistic.value_two,
        'value_three': statistic.value_three,
        'value_four': statistic.value_four,
        'caption_one': caption('caption_one'),
        'caption_two': caption('caption_two'),
        'caption_three': caption('caption_three'),
        'caption_four': caption('caption_four'),
        'icon_one': _stat_icon(statistic.icon_one, STAT_ICON_DEFAULTS[0]),
        'icon_two': _stat_icon(statistic.icon_two, STAT_ICON_DEFAULTS[1]),
        'icon_three': _stat_icon(statistic.icon_three, STAT_ICON_DEFAULTS[2]),
        'icon_four': _stat_icon(statistic.icon_four, STAT_ICON_DEFAULTS[3]),
        'cards': cards,
    }


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_faqs(lang='az', on_main_page=None):
    queryset = FAQ.objects.filter(is_active=True)
    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)
    return list(queryset.order_by('sort_order', 'id'))


def serialize_faq(faq, lang='az'):
    if faq is None:
        return None
    return {
        'id': faq.id,
        'question': _localized_with_az_fallback(faq, lang, 'question'),
        'answer': _localized_with_az_fallback(faq, lang, 'answer'),
    }


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

def get_blogs(lang='az'):
    return Blog.objects.all().order_by('-date', '-created_at')


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_blog_by_id(blog_id):
    try:
        return Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return None


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_blog_by_slug(slug):
    try:
        return Blog.objects.get(slug=slug)
    except Blog.DoesNotExist:
        return None


def get_other_blogs(blog_id, lang='az', limit=6):
    """Other posts for detail sidebar (newest first), excluding the current post."""
    qs = Blog.objects.exclude(pk=blog_id).order_by('-date', '-created_at')[:limit]
    return [serialize_blog(b, lang) for b in qs]


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def parse_bullet_list(text):
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def serialize_service(service, lang='az'):
    if service is None:
        return None

    bullet_field = get_localized_field_name('bullet_list', lang)
    bullet_raw = getattr(service, bullet_field, None) or service.bullet_list_az
    medias = [
        {
            'id': media.id,
            'image': media.image.url if media.image else None,
            'video': media.video.url if media.video else None,
        }
        for media in service.medias.all()
    ]
    images = [m['image'] for m in medias if m['image']]
    videos = [m['video'] for m in medias if m['video']]
    raw_description = _localized_with_az_fallback(service, lang, 'description')
    description_html = prepare_rich_html(raw_description)
    description_preview_html = build_about_description_preview(description_html, word_count=22)

    return {
        'id': service.id,
        'slug': service.slug,
        'name': _localized_with_az_fallback(service, lang, 'name') or service.name_az,
        'description': raw_description,
        'description_html': mark_safe(description_html),
        'description_preview': mark_safe(description_preview_html),
        'bullet_items': parse_bullet_list(bullet_raw),
        'is_active': service.is_active,
        'on_main_page': service.on_main_page,
        'created_at': service.created_at,
        'medias': medias,
        'images': images,
        'cover_image': images[0] if images else None,
        'gallery_images': images[1:],
        'videos': videos,
    }


def serialize_package(package, lang='az'):
    if package is None:
        return None

    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)

    services = package.service.filter(is_active=True)

    desc = getattr(package, desc_field, package.description_az) or ''
    description_html = prepare_rich_html(desc)

    return {
        'id': package.id,
        'name': getattr(package, name_field, package.name_az),
        'description': desc,
        'description_html': mark_safe(description_html),
        'price': package.price,
        'currency': package.currency,
        'price_from': package.price_from,
        'price_display': (
            format_package_price(
                package.price,
                package.currency,
                price_from=package.price_from,
                lang=lang,
            )
            if package.price is not None
            else None
        ),
        'image': package.image.url if package.image else None,
        'end_date': package.end_date,
        'is_active': package.is_active,
        'created_at': package.created_at,
        'services': [serialize_service(s, lang) for s in services],
    }


def serialize_about(about, lang='az'):
    if about is None:
        return None

    main_title_field = get_localized_field_name('main_title', lang)
    second_title_field = get_localized_field_name('second_title', lang)
    desc_field = get_localized_field_name('description', lang)

    gallery_images = [m.image.url for m in about.medias.all() if m.image]

    first_image = gallery_images[0] if gallery_images else None
    if not first_image and about.video_poster:
        first_image = about.video_poster.url

    description_html = prepare_rich_html(
        getattr(about, desc_field, about.description_az) or ''
    )
    description_preview_html = build_about_description_preview(description_html)

    return {
        'id': about.id,
        'main_title': getattr(about, main_title_field, about.main_title_az),
        'second_title': getattr(about, second_title_field, about.second_title_az),
        'description': mark_safe(description_html),
        'description_preview': mark_safe(description_preview_html),
        'video': about.video.url if about.video else None,
        'video_poster': about.video_poster.url if about.video_poster else None,
        'first_image': first_image,
        'gallery_images': gallery_images,
    }


def serialize_partner(partner, lang='az'):
    if partner is None:
        return None

    name_field = get_localized_field_name('name', lang)
    media = partner.medias.first()

    return {
        'id': partner.id,
        'name': getattr(partner, name_field, partner.name_az),
        'instagram': partner.instagram,
        'facebook': partner.facebook,
        'linkedn': partner.linkedn,
        'is_active': partner.is_active,
        'created_at': partner.created_at,
        'logo': media.image.url if media and media.image else None,
    }


def _normalize_phone_digits(number):
    if not number:
        return None
    digits = re.sub(r'\D', '', str(number).strip())
    if not digits:
        return None
    if digits.startswith('994'):
        return digits
    if digits.startswith('0'):
        return '994' + digits[1:]
    if len(digits) == 9:
        return '994' + digits
    return digits


def _build_whatsapp_url(number):
    digits = _normalize_phone_digits(number)
    if not digits:
        return None
    return f'https://wa.me/{digits}'


def _build_tel_url(number):
    digits = _normalize_phone_digits(number)
    if not digits:
        return None
    return f'tel:+{digits}'


def serialize_contact(contact, lang='az'):
    if contact is None:
        return None

    address_field = get_localized_field_name('address', lang)
    whatsapp_raw = (contact.whatsapp_number or '').strip()
    map_embed = (contact.map_embed_url or '').strip()
    map_url = map_embed.replace('/maps/embed', '/maps', 1) if map_embed else ''

    return {
        'id': contact.id,
        'address': getattr(contact, address_field, contact.address_az),
        'phone': contact.phone,
        'phone_tel': _build_tel_url(contact.phone),
        'whatsapp_number': whatsapp_raw,
        'whatsapp_url': _build_whatsapp_url(whatsapp_raw),
        'email': contact.email,
        'email_two': contact.email_two,
        'instagram': contact.instagram,
        'facebook': contact.facebook,
        'youtube': contact.youtube,
        'linkedn': contact.linkedn,
        'tiktok': contact.tiktok,
        'map_embed_url': map_embed,
        'map_url': map_url,
    }


def serialize_blog(blog, lang='az'):
    if blog is None:
        return None

    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)
    raw_description = getattr(blog, desc_field, None) or blog.description_az or ''
    description_html = prepare_rich_html(raw_description)
    description_preview_html = build_about_description_preview(description_html, word_count=25)

    return {
        'id': blog.id,
        'slug': blog.slug,
        'name': getattr(blog, name_field, blog.name_az),
        'topic': _localized_with_az_fallback(blog, lang, 'topic'),
        'description': mark_safe(description_html),
        'description_preview': mark_safe(description_preview_html),
        'image': blog.image.url if blog.image else None,
        'date': blog.date,
        'view_count': blog.view_count,
        'created_at': blog.created_at,
    }


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

_REVIEW_CARD_BACKGROUNDS = (
    '#eef4ff', '#fff0f3', '#ecfdf5', '#fef9ee', '#f5f3ff', '#e0f7fa',
    '#fdf4ff', '#fff7ed', '#f0fdf4', '#fef2f2',
)
_REVIEW_STAR_COLORS = (
    '#f59e0b', '#ef4444', '#8b5cf6', '#059669', '#2563eb', '#db2777',
    '#d97706', '#0d9488', '#7c3aed', '#ea580c',
)


def _review_card_theme(review_id):
    """Stable per-review visuals: card bg and star tint."""
    seed = (review_id or 0) * 7919 + 104729
    card_bg = _REVIEW_CARD_BACKGROUNDS[seed % len(_REVIEW_CARD_BACKGROUNDS)]
    star_color = _REVIEW_STAR_COLORS[(seed // 7) % len(_REVIEW_STAR_COLORS)]
    return card_bg, star_color


def get_active_reviews(limit=20):
    return list(
        Review.objects.filter(is_active=True)
        .select_related('service', 'package')
        .order_by('-created_at')[:limit]
    )


def _serialize_review_target(review, lang='az'):
    if review.service_id and review.service:
        name_field = get_localized_field_name('name', lang)
        return {
            'type': 'service',
            'id': review.service.id,
            'name': getattr(review.service, name_field, review.service.name_az),
            'slug': review.service.slug,
        }
    if review.package_id and review.package:
        name_field = get_localized_field_name('name', lang)
        return {
            'type': 'package',
            'id': review.package.id,
            'name': getattr(review.package, name_field, review.package.name_az),
            'icon_gradient': TYPE_HEADER_GRADIENTS['plane'],
        }
    return None


def serialize_review(review, lang='az'):
    """Public testimonial data — email intentionally omitted."""
    if review is None:
        return None
    rating = max(1, min(5, review.rating))
    card_bg, star_color = _review_card_theme(review.id)
    return {
        'id': review.id,
        'name': review.name,
        'message': review.message,
        'rating': rating,
        'rating_range': range(rating),
        'empty_stars': range(5 - rating),
        'card_bg': card_bg,
        'star_color': star_color,
        'target': _serialize_review_target(review, lang),
        'created_at': review.created_at,
    }


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------

def paginate_queryset(queryset, page, per_page):
    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj, paginator


def get_pagination_data(page_obj, paginator):
    return {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
        'per_page': paginator.per_page,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page_range': list(paginator.page_range),
    }


# ---------------------------------------------------------------------------
# Page-level data builders
# ---------------------------------------------------------------------------

@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_home_page_data(request, lang):
    is_active = request.GET.get('is_active', 'true').lower() == 'true'

    services = list(
        get_services(lang=lang, is_active=is_active, on_main_page=True)[:6]
    )
    packages = list(get_packages(lang=lang, is_active=is_active))
    serialized_services = [serialize_service(s, lang) for s in services]
    serialized_packages = [serialize_package(p, lang) for p in packages]

    all_partners = get_partners(lang=lang, is_active=True)
    serialized_partners = [serialize_partner(p, lang) for p in all_partners]

    about = get_about(lang)
    contact = get_contact(lang)
    about_data = serialize_about(about, lang) if about else None
    hero_carousel = build_hero_carousel(lang)

    blog_list = list(
        Blog.objects.filter(on_main_page=True).order_by('-date', '-created_at')[:6]
    )
    home_blogs = [serialize_blog(b, lang) for b in blog_list]

    faq_list = get_faqs(lang, on_main_page=True)[:6]
    if not faq_list:
        faq_list = get_faqs(lang)[:6]
    home_faqs = [serialize_faq(f, lang) for f in faq_list]

    reviews = [serialize_review(r, lang) for r in get_active_reviews(limit=20)]

    return {
        'services': serialized_services,
        'packages': serialized_packages,
        'partners': serialized_partners,
        'about': about_data,
        'contact': serialize_contact(contact, lang) if contact else None,
        'filters': {
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_carousel': hero_carousel,
        'statistics': get_statistics(lang),
        'home_blogs': home_blogs,
        'faqs': home_faqs,
        'reviews': reviews,
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_service_list_data(request, lang):
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    page = request.GET.get('page', 1)
    per_page_param = request.GET.get('per_page')

    services = get_services(lang=lang, is_active=is_active)

    if per_page_param is None:
        per_page = 9
    else:
        per_page = int(per_page_param)

    services_page_obj, services_paginator = paginate_queryset(services, page, per_page)
    serialized_services = [serialize_service(s, lang) for s in services_page_obj]

    contact = get_contact(lang)

    return {
        'services': serialized_services,
        'contact': serialize_contact(contact, lang) if contact else None,
        'pagination': get_pagination_data(services_page_obj, services_paginator),
        'filters': {
            'is_active': is_active,
        },
        'background_image': get_background_image('service'),
        'page_heading': _('Services'),
        'page_motto': get_page_motto('service', lang),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_blog_list_data(request, lang):
    page = request.GET.get('page', 1)
    per_page = 6

    blogs = get_blogs(lang=lang)
    blogs_page_obj, blogs_paginator = paginate_queryset(blogs, page, per_page)
    serialized_blogs = [serialize_blog(b, lang) for b in blogs_page_obj]

    contact = get_contact(lang)

    page_heading = _('Blog')

    return {
        'blogs': serialized_blogs,
        'contact': serialize_contact(contact, lang) if contact else None,
        'pagination': get_pagination_data(blogs_page_obj, blogs_paginator),
        'page_heading': page_heading,
        'page_motto': get_page_motto('blog', lang),
    }
