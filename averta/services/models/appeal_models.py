from django.db import models
from django.core.validators import MaxLengthValidator


class AppealContact(models.Model):
    full_name = models.CharField(
        max_length=255,
        verbose_name='Ad soyad'
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=40,
        blank=True,
        default='',
        verbose_name='Mobil nömrə',
    )
    subject = models.CharField(
        max_length=250,
        verbose_name='Mövzu'
    )
    info = models.TextField(
        validators=[MaxLengthValidator(500)],
        verbose_name='Mesaj'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Oxunub?',
        help_text='Mesajı oxuduqdan sonra işarələyin.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Gələn mesaj (əlaqə forması)'
        verbose_name_plural = 'Gələn mesajlar (əlaqə forması)'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.subject}"
