from django.db import models
from django.core.validators import MaxLengthValidator


class Package(SluggedModel):
    service = models.ManyToManyField(
        'Service',
        related_name='packages',  
        verbose_name='Xidmətlər',
        help_text='Bu paketə daxil olan xidmətləri seçin. Saytda paketlər xidmətlər ilə birlikdə göstəriləcək, ona görə də ən azı bir xidmət seçmək tövsiyə olunur.'
        null=True,
        blank=True,
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
    price=models.DecimalField(
        max_digits=20000,
        decimal_places=2,
        verbose_name='Qiymət',
        null=True,
        blank=True,
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
        help_text='Bu tarix keçdikdən sonra paket avtomatik olaraq saytda görünməz olacaq. Boş buraxsanız, paket müddətsiz olacaq.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Paket'
        verbose_name_plural = 'Paketlər'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name_az or 'Paket'