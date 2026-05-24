from django.db import models
from django.core.validators import MaxLengthValidator

from services.utils import SluggedModel


class Package(SluggedModel):
    CURRENCY_AZN = 'AZN'
    CURRENCY_USD = 'USD'
    CURRENCY_EUR = 'EUR'
    CURRENCY_CHOICES = [
        (CURRENCY_AZN, 'AZN (₼)'),
        (CURRENCY_USD, 'USD ($)'),
        (CURRENCY_EUR, 'EUR (€)'),
    ]

    ICON_PLANE    = 'plane'
    ICON_HIKE     = 'hike'
    ICON_MOUNTAIN = 'mountain'
    ICON_COMPASS  = 'compass'
    ICON_BEACH    = 'beach'
    ICON_BOAT     = 'boat'
    ICON_CAMERA   = 'camera'
    ICON_CITY     = 'city'
    ICON_CAR      = 'car'
    ICON_TENT     = 'tent'
    ICON_CHOICES = [
        (ICON_PLANE,    '✈ Təyyarə'),
        (ICON_HIKE,     '🥾 Yürüyüş'),
        (ICON_MOUNTAIN, '⛰ Dağ'),
        (ICON_COMPASS,  '🧭 Kompas'),
        (ICON_BEACH,    '🏖 Çimərlik'),
        (ICON_BOAT,     '⛵ Gəmi'),
        (ICON_CAMERA,   '📷 Fototur'),
        (ICON_CITY,     '🏙 Şəhər turu'),
        (ICON_CAR,      '🚗 Avtomobil turu'),
        (ICON_TENT,     '⛺ Düşərgə'),
    ]

    service = models.ManyToManyField(
        'Service',
        related_name='packages',
        verbose_name='Xidmətlər',
        help_text=(
            'Bu paketə daxil olan xidmətləri seçin. '
            'Saytda paketlər xidmətlərlə birlikdə göstəriləcək.'
        ),
    )
    name_az = models.CharField(
        max_length=250,
        verbose_name='Paket adı (AZ)',
    )
    name_en = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Paket adı (EN)',
    )
    name_ru = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        verbose_name='Paket adı (RU)',
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(600)],
        verbose_name='Məzmun (AZ)',
        help_text='Maksimum 600 simvol. Saytda kart daxilindəki scroll bölməsində göstərilir.',
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(600)],
        verbose_name='Məzmun (EN)',
        help_text='Maksimum 600 simvol.',
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(600)],
        verbose_name='Məzmun (RU)',
        help_text='Maksimum 600 simvol.',
    )
    price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name='Qiymət',
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_AZN,
        verbose_name='Valyuta',
    )
    icon_type = models.CharField(
        max_length=20,
        choices=ICON_CHOICES,
        default=ICON_PLANE,
        verbose_name='İkon növü',
        help_text='Kart üzərindəki ikon kateqoriyası.',
    )
    icon_variant = models.CharField(
        max_length=1,
        choices=[('1', 'Stil 1'), ('2', 'Stil 2'), ('3', 'Stil 3')],
        default='1',
        verbose_name='İkon stili',
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name='Saytda göstərilsin?',
        help_text='Söndürsəniz paket saytda görünməz.',
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Paket bitiş tarixi',
        help_text=(
            'Bu tarix keçdikdən sonra paket avtomatik olaraq saytda görünməz olacaq. '
            'Boş buraxsanız, paket müddətsiz olacaq.'
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def get_slug_source(self) -> str:
        return self.name_az

    class Meta:
        verbose_name = 'Paket'
        verbose_name_plural = 'Paketlər'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name_az or 'Paket'
