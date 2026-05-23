from django.db import models


class FAQ(models.Model):
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
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Tez-tez verilən sual'
        verbose_name_plural = 'Tez-tez verilən suallar'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.question_az
