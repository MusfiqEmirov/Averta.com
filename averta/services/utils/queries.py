import html as html_lib

from django.db.models import Q, Prefetch
from django.utils import translation
from django.utils.translation import gettext as _
from django.templatetags.static import static
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from projects.models.media_models import media_not_marked_as_background_q
from projects.models import (
    Product, ProductCategory, Partner, About,
    Contact, Media, Motto, Statistic, Blog, FAQ,
)
from projects.utils.cache_utils import cached_query, get_query_cache_key, cached_page_data
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


# ---------------------------------------------------------------------------
# Product / ProductCategory
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_product_categories(lang='az'):
    return ProductCategory.objects.all().order_by('id')


def get_products(lang='az', category_slug=None, is_active=True, on_main_page=None):
    queryset = Product.objects.select_related('category').prefetch_related(
        Prefetch(
            'medias',
            queryset=Media.objects.filter(image__isnull=False).filter(
                media_not_marked_as_background_q(),
            ),
        )
    )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)

    return queryset.order_by('-created_at')


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_product_by_slug(slug, lang='az'):
    try:
        return Product.objects.select_related('category').prefetch_related(
            Prefetch(
                'medias',
                queryset=Media.objects.filter(image__isnull=False).filter(
                    media_not_marked_as_background_q(),
                ),
            )
        ).get(slug=slug, is_active=True)
    except Product.DoesNotExist:
        return None


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
            ).filter(media_not_marked_as_background_q()),
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
        'product': 'is_product_page_background_image',
        'blog': 'is_blog_page_background_image',
    }

    if page_type not in image_map:
        return None

    media = Media.objects.filter(**{image_map[page_type]: True}).first()
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

HERO_FALLBACK_IMAGE_PATHS = (
    'assets/img/hero_1.jpg',
    'assets/img/hero_2.jpg',
    'assets/img/hero_3.jpg',
)


PAGE_MOTTO_FLAGS = {
    'about': 'is_about_page',
    'contact': 'is_contact_page',
    'product': 'is_product_page',
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
    return [
        getattr(m, text_field, m.text_az)
        for m in Motto.objects.filter(show_on_home_hero=True).order_by('id')
    ]


def build_hero_carousel(lang):
    motto_texts = get_motto_texts(lang)
    n_mottos = len(motto_texts)
    urls = list(get_home_background_images(limit=6))
    if not urls:
        urls = [static(p) for p in HERO_FALLBACK_IMAGE_PATHS]
    slides = []
    for i, url in enumerate(urls):
        motto = motto_texts[i % n_mottos] if n_mottos else None
        slides.append({
            'image_url': url,
            'motto': motto,
        })
    return slides


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_statistics(lang='az'):
    statistic = Statistic.objects.first()
    if statistic:

        def caption(base):
            return (_localized_with_az_fallback(statistic, lang, base) or '').strip()

        return {
            'value_one': statistic.value_one,
            'value_two': statistic.value_two,
            'value_three': statistic.value_three,
            'value_four': statistic.value_four,
            'caption_one': caption('caption_one'),
            'caption_two': caption('caption_two'),
            'caption_three': caption('caption_three'),
            'caption_four': caption('caption_four'),
        }
    return {}


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_faqs(lang='az'):
    return FAQ.objects.filter(is_active=True).order_by('sort_order', 'id')


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


def get_other_blogs(blog_id, lang='az', limit=12):
    """Other posts for detail sidebar (newest first), excluding the current post."""
    qs = Blog.objects.exclude(pk=blog_id).order_by('-date', '-created_at')[:limit]
    return [serialize_blog(b, lang) for b in qs]


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def serialize_product(product, lang='az'):
    if product is None:
        return None

    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)
    cat_name_field = get_localized_field_name('name', lang)

    return {
        'id': product.id,
        'slug': product.slug,
        'name': getattr(product, name_field, product.name_az),
        'description': getattr(product, desc_field, product.description_az),
        'is_active': product.is_active,
        'on_main_page': product.on_main_page,
        'created_at': product.created_at,
        'category': {
            'id': product.category.id,
            'slug': product.category.slug,
            'name': getattr(product.category, cat_name_field, product.category.name_az),
        },
        'medias': [
            {
                'id': media.id,
                'image': media.image.url if media.image else None,
                'video': media.video.url if media.video else None,
            }
            for media in product.medias.all()
        ]
    }


def serialize_product_category(category, lang='az'):
    name_field = get_localized_field_name('name', lang)
    return {
        'id': category.id,
        'slug': category.slug,
        'name': getattr(category, name_field, category.name_az),
    }


def serialize_about(about, lang='az'):
    if about is None:
        return None

    main_title_field = get_localized_field_name('main_title', lang)
    second_title_field = get_localized_field_name('second_title', lang)
    desc_field = get_localized_field_name('description', lang)

    return {
        'id': about.id,
        'main_title': getattr(about, main_title_field, about.main_title_az),
        'second_title': getattr(about, second_title_field, about.second_title_az),
        'description': html_lib.unescape(getattr(about, desc_field, about.description_az) or ''),
        'video': about.video.url if about.video else None,
        'video_poster': about.video_poster.url if about.video_poster else None,
        'medias': [
            {
                'id': media.id,
                'name': _localized_with_az_fallback(media, lang, 'name'),
                'short_description': _localized_with_az_fallback(
                    media, lang, 'short_description'
                ),
                'image': media.image.url if media.image else None,
            }
            for media in about.medias.all()
            if media.image
        ]
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


def serialize_contact(contact, lang='az'):
    if contact is None:
        return None

    address_field = get_localized_field_name('address', lang)

    return {
        'id': contact.id,
        'address': getattr(contact, address_field, contact.address_az),
        'phone': contact.phone,
        'whatsapp_number': contact.whatsapp_number,
        'email': contact.email,
        'email_two': contact.email_two,
        'instagram': contact.instagram,
        'facebook': contact.facebook,
        'youtube': contact.youtube,
        'linkedn': contact.linkedn,
        'tiktok': contact.tiktok,
        'map_embed_url': (contact.map_embed_url or '').strip(),
    }


def serialize_blog(blog, lang='az'):
    if blog is None:
        return None

    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)

    return {
        'id': blog.id,
        'name': getattr(blog, name_field, blog.name_az),
        'description': getattr(blog, desc_field, blog.description_az),
        'image': blog.image.url if blog.image else None,
        'date': blog.date,
        'view_count': blog.view_count,
        'created_at': blog.created_at,
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
    category_slug = request.GET.get('slug')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    special_filter = request.GET.get('special')

    if special_filter == 'true':
        products = get_products(
            lang=lang,
            is_active=is_active,
            on_main_page=True,
        )[:9]
    else:
        all_main_page_products = get_products(
            lang=lang,
            is_active=is_active,
            on_main_page=True,
        )

        from collections import defaultdict
        products_by_category = defaultdict(list)
        for product in all_main_page_products:
            cat_id = product.category_id
            if len(products_by_category[cat_id]) < 6:
                products_by_category[cat_id].append(product)

        products = []
        for cat_id in sorted(products_by_category.keys()):
            products.extend(products_by_category[cat_id])

    serialized_products = [serialize_product(p, lang) for p in products]

    categories = get_product_categories(lang)
    serialized_categories = [serialize_product_category(c, lang) for c in categories]

    # Attach cover image to each category from on_main_page products (no extra DB hit)
    cat_cover = {}
    for p in serialized_products:
        cid = p['category']['id']
        if cid not in cat_cover and p['medias']:
            cat_cover[cid] = p['medias'][0]['image']
    for cat in serialized_categories:
        cat['cover_image'] = cat_cover.get(cat['id'])

    # Build per-category panels for the home page split layout
    from collections import defaultdict as _dd
    _cat_prods = _dd(list)
    for p in serialized_products:
        _cat_prods[p['category']['id']].append(p)
    category_panels = [
        {'category': cat, 'products': _cat_prods[cat['id']][:6]}
        for cat in serialized_categories
        if _cat_prods.get(cat['id'])
    ]

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

    faq_list = get_faqs(lang)
    home_faqs = [serialize_faq(f, lang) for f in faq_list]

    return {
        'products': serialized_products,
        'categories': serialized_categories,
        'partners': serialized_partners,
        'about': about_data,
        'contact': serialize_contact(contact, lang) if contact else None,
        'filters': {
            'slug': category_slug,
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_carousel': hero_carousel,
        'statistics': get_statistics(lang),
        'category_panels': category_panels,
        'home_blogs': home_blogs,
        'faqs': home_faqs,
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_product_list_data(request, lang):
    category_slug = request.GET.get('slug')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'
    page = request.GET.get('page', 1)
    per_page_param = request.GET.get('per_page')

    products = get_products(
        lang=lang,
        category_slug=category_slug,
        is_active=is_active,
    )

    if per_page_param is None:
        per_page = 9
    else:
        per_page = int(per_page_param)

    products_page_obj, products_paginator = paginate_queryset(products, page, per_page)
    serialized_products = [serialize_product(p, lang) for p in products_page_obj]

    categories = get_product_categories(lang)
    serialized_categories = [serialize_product_category(c, lang) for c in categories]

    selected_category = None
    if category_slug:
        category_obj = next((c for c in categories if c.slug == category_slug), None)
        if category_obj:
            selected_category = serialize_product_category(category_obj, lang)

    contact = get_contact(lang)

    page_heading = selected_category['name'] if selected_category else None
    if not page_heading:
        page_heading = _('Products')

    return {
        'products': serialized_products,
        'categories': serialized_categories,
        'selected_category': selected_category,
        'contact': serialize_contact(contact, lang) if contact else None,
        'pagination': get_pagination_data(products_page_obj, products_paginator),
        'filters': {
            'slug': category_slug,
            'is_active': is_active,
        },
        'background_image': get_background_image('product'),
        'page_heading': page_heading,
        'page_motto': get_page_motto('product', lang),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_blog_list_data(request, lang):
    page = request.GET.get('page', 1)
    per_page = 9

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
