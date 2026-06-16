from django.db import models
from django.core.validators import MaxLengthValidator

from services.utils import SluggedModel, UpdatedAtMixin


class Package(SluggedModel, UpdatedAtMixin):
    CURRENCY_AZN = 'AZN'
    CURRENCY_USD = 'USD'
    CURRENCY_EUR = 'EUR'
    CURRENCY_CHOICES = [
        (CURRENCY_AZN, 'AZN (₼)'),
        (CURRENCY_USD, 'USD ($)'),
        (CURRENCY_EUR, 'EUR (€)'),
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
    image = models.ImageField(
        upload_to='images/packages/',
        null=True,
        blank=True,
        verbose_name='Şəkil',
        help_text='Paket kartının yuxarı hissəsində göstərilir.',
    )
    price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name='Qiymət',
    )
    price_from = models.BooleanField(
        default=False,
        verbose_name='Qiymətə «dan/dən» əlavə et',
        help_text='İşarələnərsə saytda qiymət «$909-dan», «€907-dən» kimi göstərilir.',
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_AZN,
        verbose_name='Valyuta',
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
