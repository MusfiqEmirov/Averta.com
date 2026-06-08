from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models

REVIEW_NAME_MAX_LENGTH = 50
REVIEW_MESSAGE_MAX_LENGTH = 190


class Review(models.Model):
    name = models.CharField(
        max_length=REVIEW_NAME_MAX_LENGTH,
        verbose_name='Name',
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Email',
        blank=True,
        default='',
    )
    phone = models.CharField(
        max_length=40,
        blank=True,
        default='',
        verbose_name='Mobil nömrə',
    )
    message = models.TextField(
        validators=[MaxLengthValidator(REVIEW_MESSAGE_MAX_LENGTH)],
        verbose_name='Review',
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name='Rating (1–5)',
        help_text='Stars from 1 to 5.',
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='Xidmət',
    )
    package = models.ForeignKey(
        'Package',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='Paket',
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Active',
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Oxunub?',
        help_text='Rəyi oxuduqdan sonra işarələyin.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )

    class Meta:
        verbose_name = 'Rəy'
        verbose_name_plural = 'Rəylər'
        ordering = ('-created_at',)

    def clean(self):
        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValidationError({'rating': 'Reytinq 1 ilə 5 arasında olmalıdır.'})
        if self.name:
            self.name = self.name.strip()
        if self.email:
            self.email = self.email.strip().lower()
        if self.phone:
            self.phone = self.phone.strip()
        if self.message:
            self.message = self.message.strip()
        if self.service_id and self.package_id:
            raise ValidationError(
                'Yalnız xidmət və ya paket seçilməlidir, hər ikisi yox.'
            )

    def __str__(self):
        return self.name
