from django.db import models
from django.db.models import Q
from django.core.files.storage import default_storage
import logging

from .service_models import Service
from .package_models import Package
from .partner_models import Partner
from .about_models import About

logger = logging.getLogger(__name__)


def media_not_marked_as_background_q():
    """Filter for content media only (exclude rows flagged as page background images)."""
    return (
        Q(is_home_page_background_image=False)
        & Q(is_about_page_background_image=False)
        & Q(is_contact_page_background_image=False)
        & Q(is_service_page_background_image=False)
        & Q(is_blog_page_background_image=False)
        & Q(is_home_contact_background_image=False)
        & Q(is_contact_booking_background_image=False)
    )


from services.utils import UpdatedAtMixin


class Media(UpdatedAtMixin, models.Model):
    about = models.ForeignKey(
        About,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Haqqimizda'
    )
    service = models.ForeignKey(
        Service,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Xidmet'
    )
    package = models.ForeignKey(
        Package,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Paket',
    )
    partner = models.ForeignKey(
        Partner,
        related_name='medias',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Terefdasl'
    )
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Sekil'
    )
    video = models.FileField(
        upload_to='videos/',
        null=True,
        blank=True,
        verbose_name='Video'
    )
    is_home_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Ana sehife fon sekli'
    )
    is_about_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Haqqimizda sehifesi fon sekli'
    )
    is_contact_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Elaqe sehifesi fon sekli'
    )
    is_service_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Xidmetler sehifesi fon sekli'
    )
    is_blog_page_background_image = models.BooleanField(
        default=False,
        verbose_name='Bloq sehifeleri fon sekli'
    )
    is_home_contact_background_image = models.BooleanField(
        default=False,
        verbose_name='Ana sehife Elaqe bolmesi fon sekli'
    )
    is_contact_booking_background_image = models.BooleanField(
        default=False,
        verbose_name='Elaqe sehifesi Sifaris et bolmesi fonu'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaradilma tarixi'
    )

    class Meta:
        verbose_name = 'Sehife banner fon sekli'
        verbose_name_plural = 'Sehife banner fon sekilleri'

    @property
    def webp_url(self):
        return self.image.url

    def delete_files(self):
        if not self.image:
            return

        image_name = self.image.name
        image_id = self.pk

        logger.info(f"[MEDIA DELETE] Deleting files (ID: {image_id}, File: {image_name})")

        try:
            storage = default_storage

            if image_name.lower().endswith('.webp'):
                base_name = image_name.rsplit('.', 1)[0]
                for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                    original_name = base_name + ext
                    if storage.exists(original_name):
                        try:
                            storage.delete(original_name)
                        except Exception as e:
                            logger.error(f"[MEDIA DELETE] Error deleting original ({original_name}): {e}")

                if storage.exists(image_name):
                    storage.delete(image_name)
            else:
                webp_name = image_name.rsplit('.', 1)[0] + '.webp'
                if storage.exists(webp_name):
                    try:
                        storage.delete(webp_name)
                    except Exception as e:
                        logger.error(f"[MEDIA DELETE] Error deleting webp ({webp_name}): {e}")

                if storage.exists(image_name):
                    storage.delete(image_name)

        except Exception as e:
            logger.error(f"[MEDIA DELETE] Error occurred (ID: {image_id}): {e}")

    def delete(self, *args, **kwargs):
        self.delete_files()
        super().delete(*args, **kwargs)
