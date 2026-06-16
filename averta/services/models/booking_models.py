from django.db import models
from django.core.validators import MaxLengthValidator


from services.utils import UpdatedAtMixin


class Booking(UpdatedAtMixin, models.Model):
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='bookings',
        verbose_name='Xidmətlər',
    )
    packages = models.ManyToManyField(
        'Package',
        blank=True,
        related_name='bookings',
        verbose_name='Paketlər',
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name='Ad soyad',
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='Email',
    )
    phone = models.CharField(
        max_length=40,
        verbose_name='Mobil nömrə',
    )
    date_from = models.DateField(
        null=True,
        blank=True,
        verbose_name='Gediş tarixi',
        help_text='Səyahətin gediş tarixi.',
    )
    date_to = models.DateField(
        null=True,
        blank=True,
        verbose_name='Qayıdış tarixi',
        help_text='Səyahətin qayıdış tarixi.',
    )
    note = models.TextField(
        validators=[MaxLengthValidator(600)],
        null=True,
        blank=True,
        verbose_name='Mesaj',
    )
    adults_count = models.PositiveIntegerField(
        default=1,
        verbose_name='Böyük sayı',
    )
    children_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Uşaq sayı',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Oxunub?',
        help_text='Sifarişi oxuduqdan sonra işarələyin.',
    )
    is_customer = models.BooleanField(
        default=False,
        verbose_name='Müştərimizdir?',
        help_text='Bu şəxsin artıq müştəri olub olmadığını işarələyin',
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Silinib?',
        help_text='Sifarişi silmək əvəzinə “Silinib?” kimi işarələyin.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Sifariş'
        verbose_name_plural = 'Sifarişlər'
        ordering = ['-created_at']

    def __str__(self):
        labels = [str(s) for s in self.services.all()[:2]]
        labels += [str(p) for p in self.packages.all()[:2]]
        if labels:
            suffix = ', '.join(labels)
            extra = self.services.count() + self.packages.count() - len(labels)
            if extra > 0:
                suffix += f' (+{extra})'
            return f'{self.full_name} — {suffix}'
        return self.full_name
