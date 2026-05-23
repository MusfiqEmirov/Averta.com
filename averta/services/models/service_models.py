from django.db import models
from django.core.validators import MaxLengthValidator

from services.utils import SluggedModel


class ServiceCategory(SluggedModel):
    name_az = models.CharField(
        max_length=250,
        verbose_name='Kateqoriya adı (AZ)',
    )
    name_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Kateqoriya adı (EN)',
    )
    name_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Kateqoriya adı (RU)',
    )

    def get_slug_source(self) -> str:
        return self.name_az

    class Meta:
        verbose_name = 'Xidmət kateqoriyası'
        verbose_name_plural = 'Xidmət kateqoriyaları'
        ordering = ['id']

    def __str__(self):
        return self.name_az


class Service(SluggedModel):
    category = models.ForeignKey(
        ServiceCategory,
        related_name='services',
        on_delete=models.CASCADE,
        verbose_name='Kateqoriya',
    )
    name_az = models.CharField(
        max_length=250,
        verbose_name='Xidmət adı (AZ)',
    )
    name_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Xidmət adı (EN)',
    )
    name_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Xidmət adı (RU)',
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(500)],
        verbose_name='Xidmət haqqında (AZ)',
    )
    description_en = models.TextField(
        validators=[MaxLengthValidator(500)],
        null=True,
        blank=True,
        verbose_name='Xidmət haqqında (EN)',
    )
    description_ru = models.TextField(
        validators=[MaxLengthValidator(500)],
        null=True,
        blank=True,
        verbose_name='Xidmət haqqında (RU)',
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name='Saytda göstərilsin?',
        help_text='Söndürsəniz xidmət saytda görünməz.',
    )
    on_main_page = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name='Ana səhifədə göstərilsin?',
        help_text='Hər kateqoriyada ana səhifədə ən çox 6 xidmət ola bilər.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def get_slug_source(self) -> str:
        return self.name_az

    class Meta:
        verbose_name = 'Xidmət'
        verbose_name_plural = 'Xidmətlər'
        ordering = ['-created_at']

    def __str__(self):
        return self.name_az
