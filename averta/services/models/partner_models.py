from django.db import models
from django.core.validators import MaxLengthValidator


class Partner(models.Model):
    name_az = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Tərəfdaş adı (AZ)'
    )
    name_en = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Tərəfdaş adı (EN)'
    )
    name_ru = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(120)],
        verbose_name='Tərəfdaş adı (RU)'
    )
    instagram = models.URLField(
        null=True,
        blank=True,
        verbose_name='Instagram'
    )
    facebook = models.URLField(
        null=True,
        blank=True,
        verbose_name='Facebook'
    )
    linkedn = models.URLField(
        null=True,
        blank=True,
        verbose_name='LinkedIn'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Saytda göstərilsin?',
        help_text='Söndürsəniz tərəfdaş karuseldə görünməz.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Tərəfdaş'
        verbose_name_plural = 'Tərəfdaşlar'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name_az or 'Tərəfdaş'
