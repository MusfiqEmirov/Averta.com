from django.db.models import F
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from services.models import (
    About,
    Blog,
    Contact,
    FAQ,
    Media,
    Motto,
    Package,
    Partner,
    Review,
    Service,
    Statistic,
)
from services.utils.cache_utils import invalidate_model_cache

_MEDIA_BACKGROUND_FIELDS = (
    'is_home_page_background_image',
    'is_about_page_background_image',
    'is_contact_page_background_image',
    'is_service_page_background_image',
    'is_blog_page_background_image',
    'is_home_contact_background_image',
    'is_contact_booking_background_image',
)


def _media_affects_site_cache(instance):
    """True when media is linked to content or used as a page background."""
    if any(
        (
            instance.about_id,
            instance.service_id,
            instance.package_id,
            instance.partner_id,
        )
    ):
        return True
    return any(getattr(instance, field, False) for field in _MEDIA_BACKGROUND_FIELDS)


# ---------------------------------------------------------------------------
# Ana səhifə və digər səhifələr (xidmət, paket, partnyor, bloq, əlaqə)
# ---------------------------------------------------------------------------

def _shift_sort_order(model, instance, field='sort_order'):
    new_order = getattr(instance, field)
    exclude_pk = instance.pk or 0
    if model.objects.exclude(pk=exclude_pk).filter(**{field: new_order}).exists():
        model.objects.exclude(pk=exclude_pk).filter(
            **{f'{field}__gte': new_order}
        ).update(**{field: F(field) + 1})


@receiver(pre_save, sender=Service)
def auto_shift_service_sort_order(sender, instance, **kwargs):
    _shift_sort_order(Service, instance)


@receiver(pre_save, sender=Package)
def auto_shift_package_sort_order(sender, instance, **kwargs):
    _shift_sort_order(Package, instance)


@receiver([post_save, post_delete], sender=Service)
def invalidate_service_cache(sender, **kwargs):
    invalidate_model_cache('Service')


@receiver([post_save, post_delete], sender=Package)
def invalidate_package_cache(sender, **kwargs):
    invalidate_model_cache('Package')


@receiver(m2m_changed, sender=Package.service.through)
def invalidate_package_services_m2m(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        invalidate_model_cache('Package')


@receiver([post_save, post_delete], sender=Partner)
def invalidate_partner_cache(sender, **kwargs):
    invalidate_model_cache('Partner')


@receiver([post_save, post_delete], sender=Blog)
def invalidate_blog_cache(sender, **kwargs):
    invalidate_model_cache('Blog')


@receiver([post_save, post_delete], sender=Contact)
def invalidate_contact_cache(sender, **kwargs):
    invalidate_model_cache('Contact')


# ---------------------------------------------------------------------------
# About, FAQ, hero (motto), statistika, media
# ---------------------------------------------------------------------------

@receiver([post_save, post_delete], sender=About)
def invalidate_about_cache(sender, **kwargs):
    invalidate_model_cache('About')


@receiver([post_save, post_delete], sender=Media)
def invalidate_media_cache(sender, instance, **kwargs):
    if _media_affects_site_cache(instance):
        invalidate_model_cache('Media')


@receiver([post_save, post_delete], sender=Statistic)
def invalidate_statistic_cache(sender, **kwargs):
    invalidate_model_cache('Statistic')


@receiver([post_save, post_delete], sender=Motto)
def invalidate_motto_cache(sender, **kwargs):
    invalidate_model_cache('Motto')


@receiver([post_save, post_delete], sender=FAQ)
def invalidate_faq_cache(sender, **kwargs):
    invalidate_model_cache('FAQ')


@receiver([post_save, post_delete], sender=Review)
def invalidate_review_cache(sender, **kwargs):
    invalidate_model_cache('Review')
