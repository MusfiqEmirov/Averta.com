from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator

from services.utils import SluggedModel


class Blog(SluggedModel):
    name_az = models.CharField(
        max_length=255,
        verbose_name='Başlıq (AZ)'
    )
    name_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Başlıq (EN)'
    )
    name_ru = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Başlıq (RU)'
    )
    topic_az = models.CharField(
        max_length=255,
        verbose_name='Mövzu (AZ)',
        help_text='Kartda və yazı səhifəsində başlığın üstündə göstərilir.',
    )
    topic_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Mövzu (EN)',
    )
    topic_ru = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Mövzu (RU)',
    )
    image = models.ImageField(
        upload_to='blog/',
        verbose_name='Şəkil'
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(5000)],
        verbose_name='Məzmun (AZ)'
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(5000)],
        verbose_name='Məzmun (EN)'
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(5000)],
        verbose_name='Məzmun (RU)'
    )
    date = models.DateField(
        verbose_name='Tarix'
    )
    on_main_page = models.BooleanField(
        default=False,
        verbose_name='Ana səhifədə göstərilsin?',
        help_text='Ana səhifədə ən çox 6 bloq yazısı göstərilir.',
    )
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Baxış sayı',
        help_text='Avtomatik sayılır — dəyişdirməyin.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Bloq yazısı'
        verbose_name_plural = 'Bloq yazıları'
        ordering = ['-date', '-created_at']

    def get_slug_source(self) -> str:
        return self.name_az

    def clean(self):
        super().clean()
        if self.on_main_page:
            qs = Blog.objects.filter(on_main_page=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= 6:
                raise ValidationError({
                    'on_main_page': (
                        'Ana səhifədə ən çox 6 bloq ola bilər. '
                        'Yeni yazını əlavə etmək üçün əvvəl mövcud sıradan birini söndürün.'
                    ),
                })

    def __str__(self):
        return self.name_az
