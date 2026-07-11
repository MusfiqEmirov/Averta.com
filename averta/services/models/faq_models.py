from django.core.exceptions import ValidationError
from django.db import models


from services.utils import UpdatedAtMixin


class FAQ(UpdatedAtMixin, models.Model):
    question_az = models.CharField(
        max_length=500,
        verbose_name='Sual (AZ)',
    )
    question_en = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Sual (EN)',
    )
    question_ru = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Sual (RU)',
    )
    answer_az = models.TextField(
        verbose_name='Cavab (AZ)',
    )
    answer_en = models.TextField(
        null=True,
        blank=True,
        verbose_name='Cavab (EN)',
    )
    answer_ru = models.TextField(
        null=True,
        blank=True,
        verbose_name='Cavab (RU)',
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Sıra nömrəsi',
        help_text='Kiçik rəqəm = siyahıda yuxarıda. Məs: 1, 2, 3...',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Saytda göstərilsin?',
    )
    on_main_page = models.BooleanField(
        default=False,
        verbose_name='Ana səhifədə göstərilsin?',
        help_text='Yalnız işarələnən suallar ana səhifə FAQ blokunda görünür (ən çox 6).',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Tez-tez verilən sual'
        verbose_name_plural = 'Tez-tez verilən suallar'
        ordering = ['sort_order', 'id']

    def clean(self):
        super().clean()
        if self.on_main_page:
            qs = FAQ.objects.filter(on_main_page=True, is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= 6:
                raise ValidationError({
                    'on_main_page': (
                        'Ana səhifədə ən çox 6 sual ola bilər. '
                        'Yenisini əlavə etmək üçün əvvəl mövcud sıradan birini söndürün.'
                    ),
                })

    def __str__(self):
        return self.question_az
