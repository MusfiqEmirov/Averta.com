from django.db import models
from django.core.validators import MaxLengthValidator, FileExtensionValidator


class About(models.Model):
    main_title_az = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Əsas başlıq (AZ)',
        help_text='Haqqımızda səhifəsində böyük başlıq.',
    )
    main_title_en = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Əsas başlıq (EN)'
    )
    main_title_ru = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name='Əsas başlıq (RU)'
    )
    second_title_az = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Alt başlıq (AZ)'
    )
    second_title_en = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Alt başlıq (EN)'
    )
    second_title_ru = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Alt başlıq (RU)'
    )
    description_az = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Mətn (AZ)',
        help_text='Şirkət haqqında əsas mətn — Haqqımızda səhifəsində və ana səhifədə qısa blokda.',
    )
    description_en = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Mətn (EN)',
    )
    description_ru = models.TextField(
        validators=[MaxLengthValidator(4000)],
        verbose_name='Mətn (RU)',
    )
    video = models.FileField(
        upload_to='videos/about/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=('mp4', 'webm', 'mov', 'ogg', 'mkv'),
                message='Allowed formats: mp4, webm, mov, ogg, mkv.',
            )
        ],
        verbose_name='Əsas tanıtım videosu',
        help_text='Haqqımızda və ana səhifədə göstərilən yeganə video. Yalnız bir fayl yükləyin.',
    )
    video_poster = models.ImageField(
        upload_to='images/about/video_posters/',
        null=True,
        blank=True,
        verbose_name='Video örtüyü (poster)',
        help_text='Video oynatılmadan əvvəl görünən şəkil.',
    )

    class Meta:
        verbose_name = 'Haqqımızda səhifəsi'
        verbose_name_plural = 'Haqqımızda səhifəsi'

    def __str__(self):
        return self.main_title_az or 'Haqqımızda'
