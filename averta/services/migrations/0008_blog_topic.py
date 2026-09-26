from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_faq_on_main_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='topic_az',
            field=models.CharField(
                default='',
                help_text='Kartda və yazı səhifəsində başlığın üstündə göstərilir.',
                max_length=255,
                verbose_name='Mövzu (AZ)',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog',
            name='topic_en',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='Mövzu (EN)',
            ),
        ),
        migrations.AddField(
            model_name='blog',
            name='topic_ru',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='Mövzu (RU)',
            ),
        ),
    ]
