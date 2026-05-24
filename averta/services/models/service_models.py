from django.db import models
from django.core.validators import MaxLengthValidator

from services.utils import SluggedModel


class Service(SluggedModel):
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
        validators=[MaxLengthValidator(5000)],
        verbose_name='Xidmət haqqında (AZ)',
    )
    description_en = models.TextField(
        validators=[MaxLengthValidator(5000)],
        null=True,
        blank=True,
        verbose_name='Xidmət haqqında (EN)',
    )
    description_ru = models.TextField(
        validators=[MaxLengthValidator(5000)],
        null=True,
        blank=True,
        verbose_name='Xidmət haqqında (RU)',
    )
    bullet_list_az = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (AZ)',
        help_text='Hər sətirdə bir maddə yazın (bullet list).',
    )
    bullet_list_en = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (EN)',
        help_text='One item per line (bullet list).',
    )
    bullet_list_ru = models.TextField(
        blank=True,
        null=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Maddələr siyahısı (RU)',
        help_text='Один пункт на строку (маркированный список).',
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
        help_text='Ana səhifədə ən çox 6 xidmət göstərilir.',
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

