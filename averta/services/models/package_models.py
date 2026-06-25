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
    sort_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='Sıra',
        help_text='0 = ilk (sayt, admin siyahısı). 1 = sonrakı və s.',
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
    show_date_from = models.BooleanField(
        default=True,
        verbose_name='Sifariş formunda gediş tarixi',
        help_text='İşarələnərsə sifariş formunda gediş tarixi sahəsi göstərilir.',
    )
    show_date_to = models.BooleanField(
        default=True,
        verbose_name='Sifariş formunda qayıdış tarixi',
        help_text='İşarələnərsə sifariş formunda qayıdış tarixi sahəsi göstərilir.',
    )
    show_arrival_date = models.BooleanField(
        default=False,
        verbose_name='Sifariş formunda gəliş tarixi',
        help_text='İşarələnərsə sifariş formunda gəliş tarixi sahəsi göstərilir.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def get_slug_source(self) -> str:
        return self.name_az

    class Meta:
        verbose_name = 'Paket'
        verbose_name_plural = 'Paketlər'
        ordering = ('sort_order', 'id')

    def __str__(self):
        return self.name_az or 'Paket'
