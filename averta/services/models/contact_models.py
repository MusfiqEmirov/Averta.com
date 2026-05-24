from django.db import models


class Contact(models.Model):
    address_az = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ünvan (AZ)',
    )
    address_en = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ünvan (EN)',
    )
    address_ru = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ünvan (RU)',
    )
    map_embed_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name='Google Xəritə embed URL',
    )
    phone = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='Telefon',
    )
    whatsapp_number = models.CharField(
        max_length=40,
        blank=True,
        verbose_name='WhatsApp nömrəsi',
    )
    email = models.EmailField(
        blank=True,
        verbose_name='E-poçt',
    )
    email_two = models.EmailField(
        blank=True,
        verbose_name='Əlavə e-poçt',
    )
    instagram = models.URLField(blank=True, verbose_name='Instagram')
    facebook = models.URLField(blank=True, verbose_name='Facebook')
    youtube = models.URLField(blank=True, verbose_name='YouTube')
    linkedn = models.URLField(blank=True, verbose_name='LinkedIn')
    tiktok = models.URLField(blank=True, verbose_name='TikTok')

    class Meta:
        verbose_name = 'Əlaqə məlumatları'
        verbose_name_plural = 'Əlaqə məlumatları'

    def __str__(self):
        return self.address_az or self.phone or self.email or 'Əlaqə'
