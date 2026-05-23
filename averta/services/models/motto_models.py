from django.db import models
from django.core.validators import MaxLengthValidator


class Motto(models.Model):
    text_az = models.TextField(
        validators=[MaxLengthValidator(220)],
        verbose_name='Deviz mətni (AZ)',
        help_text='Ana səhifə karuseli və ya səhifə bannerində görünən qısa cümlə.',
    )
    text_en = models.TextField(
        validators=[MaxLengthValidator(220)],
        null=True,
        blank=True,
        verbose_name='Deviz mətni (EN)',
    )
    text_ru = models.TextField(
        validators=[MaxLengthValidator(220)],
        null=True,
        blank=True,
        verbose_name='Deviz mətni (RU)',
    )
    show_on_home_hero = models.BooleanField(
        default=True,
        verbose_name='Ana səhifə karuselində göstər?',
        help_text='Ana səhifənin yuxarı böyük şəkil slayderində bu deviz görünür.',
    )
    is_about_page = models.BooleanField(
        default=False,
        verbose_name='Haqqımızda səhifəsinin banneri',
        help_text='Haqqımızda səhifəsinin yuxarı fon şəklinin üstündə.',
    )
    is_contact_page = models.BooleanField(
        default=False,
        verbose_name='Əlaqə səhifəsinin banneri',
    )
    is_service_page = models.BooleanField(
        default=False,
        verbose_name='Xidmətlər səhifəsinin banneri',
    )
    is_blog_page = models.BooleanField(
        default=False,
        verbose_name='Bloq səhifəsinin banneri',
    )

    class Meta:
        verbose_name = 'Deviz (slogan)'
        verbose_name_plural = 'Devizlər (sloganlar)'

    def __str__(self):
        return self.text_az[:60] if self.text_az else 'Deviz'

    @property
    def is_page_motto(self):
        return any([
            self.is_about_page,
            self.is_contact_page,
            self.is_service_page,
            self.is_blog_page,
        ])
