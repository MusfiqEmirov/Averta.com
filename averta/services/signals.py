from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from services.models import About, FAQ, Media, Motto, Statistic
from services.utils.cache_utils import invalidate_model_cache


@receiver([post_save, post_delete], sender=About)
def invalidate_about_cache(sender, **kwargs):
    invalidate_model_cache('About')


@receiver([post_save, post_delete], sender=Media)
def invalidate_about_media_cache(sender, instance, **kwargs):
    if instance.about_id:
        invalidate_model_cache('About')


@receiver([post_save, post_delete], sender=Statistic)
def invalidate_statistic_cache(sender, **kwargs):
    invalidate_model_cache('Statistic')


@receiver([post_save, post_delete], sender=Motto)
def invalidate_motto_cache(sender, **kwargs):
    invalidate_model_cache('Motto')


@receiver([post_save, post_delete], sender=FAQ)
def invalidate_faq_cache(sender, **kwargs):
    invalidate_model_cache('FAQ')
