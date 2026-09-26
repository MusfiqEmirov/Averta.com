from django.db import models


STAT_ICON_CHOICES = [
    ('fas fa-calendar-check', 'Təqvim / təcrübə'),
    ('fas fa-route', 'Marşrut / tur'),
    ('fas fa-users', 'Müştərilər / qrup'),
    ('fas fa-globe-americas', 'Beynəlxalq / dünya'),
    ('fas fa-plane', 'Uçuş / səyahət'),
    ('fas fa-hotel', 'Otel / qonaqlama'),
    ('fas fa-map-marked-alt', 'Xəritə / məkan'),
    ('fas fa-handshake', 'Tərəfdaşlıq'),
    ('fas fa-award', 'Mükafat / keyfiyyət'),
    ('fas fa-star', 'Ulduz / reytinq'),
    ('fas fa-heart', 'Məmnuniyyət'),
    ('fas fa-camera', 'Foto / xatirə'),
    ('fas fa-bus', 'Nəqliyyat'),
    ('fas fa-ship', 'Gəmi / kruiz'),
    ('fas fa-mountain', 'Təbiət / macəra'),
    ('fas fa-umbrella-beach', 'Çimərlik / istirahət'),
    ('fas fa-passport', 'Viza / sənəd'),
    ('fas fa-headset', 'Dəstək / xidmət'),
    ('fas fa-chart-line', 'Artım / statistika'),
    ('fas fa-thumbs-up', 'Tövsiyə'),
]

STAT_ICON_DEFAULTS = (
    'fas fa-calendar-check',
    'fas fa-route',
    'fas fa-users',
    'fas fa-globe-americas',
)


class Statistic(models.Model):
    icon_one = models.CharField(
        max_length=64,
        choices=STAT_ICON_CHOICES,
        blank=True,
        null=True,
        verbose_name='1-ci kart — ikon',
        help_text='Kartda görünən Font Awesome ikonu.',
    )
    value_one = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='1-ci kart — böyük rəqəm',
        help_text='Məsələn: 25 və ya 90+. Ana səhifə və Haqqımızda səhifəsində sol tərəfdəki birinci rəqəm.',
    )
    icon_two = models.CharField(
        max_length=64,
        choices=STAT_ICON_CHOICES,
        blank=True,
        null=True,
        verbose_name='2-ci kart — ikon',
    )
    value_two = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='2-ci kart — böyük rəqəm',
        help_text='Məsələn: 150 və ya 90+. İkinci statistika kartındakı rəqəm.',
    )
    icon_three = models.CharField(
        max_length=64,
        choices=STAT_ICON_CHOICES,
        blank=True,
        null=True,
        verbose_name='3-cü kart — ikon',
    )
    value_three = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='3-cü kart — böyük rəqəm',
        help_text='Məsələn: 500 və ya 90+. Üçüncü statistika kartındakı rəqəm.',
    )
    icon_four = models.CharField(
        max_length=64,
        choices=STAT_ICON_CHOICES,
        blank=True,
        null=True,
        verbose_name='4-cü kart — ikon',
    )
    value_four = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='4-ci kart — böyük rəqəm',
        help_text='Məsələn: 1000 və ya 90+. Dördüncü statistika kartındakı rəqəm.',
    )
    caption_one_az = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='1-ci kart — alt yazı (AZ)',
        help_text='Rəqəmin altında görünən qısa mətn. Məs: İllik təcrübə',
    )
    caption_one_en = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='1-ci kart — alt yazı (EN)',
        help_text='English version of the caption below the first number.',
    )
    caption_one_ru = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='1-ci kart — alt yazı (RU)',
        help_text='Русская версия подписи под первым числом.',
    )
    caption_two_az = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='2-ci kart — alt yazı (AZ)',
        help_text='Məs: Xidmət növü',
    )
    caption_two_en = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='2-ci kart — alt yazı (EN)',
    )
    caption_two_ru = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='2-ci kart — alt yazı (RU)',
    )
    caption_three_az = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='3-cü kart — alt yazı (AZ)',
        help_text='Məs: Müştəri sayı',
    )
    caption_three_en = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='3-cü kart — alt yazı (EN)',
    )
    caption_three_ru = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='3-cü kart — alt yazı (RU)',
    )
    caption_four_az = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='4-cü kart — alt yazı (AZ)',
        help_text='Məs: Layihə sayı',
    )
    caption_four_en = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='4-cü kart — alt yazı (EN)',
    )
    caption_four_ru = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='4-cü kart — alt yazı (RU)',
    )

    class Meta:
        verbose_name = 'Statistika (saylar bloku)'
        verbose_name_plural = 'Statistika (saylar bloku)'

    def __str__(self):
        return 'Sayt statistikası'
