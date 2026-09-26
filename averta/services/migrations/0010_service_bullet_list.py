from django.core.validators import MaxLengthValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_blog_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='bullet_list_az',
            field=models.TextField(
                blank=True,
                help_text='Hər sətirdə bir maddə yazın (bullet list).',
                null=True,
                validators=[MaxLengthValidator(2000)],
                verbose_name='Maddələr siyahısı (AZ)',
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='bullet_list_en',
            field=models.TextField(
                blank=True,
                help_text='One item per line (bullet list).',
                null=True,
                validators=[MaxLengthValidator(2000)],
                verbose_name='Maddələr siyahısı (EN)',
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='bullet_list_ru',
            field=models.TextField(
                blank=True,
                help_text='Один пункт на строку (маркированный список).',
                null=True,
                validators=[MaxLengthValidator(2000)],
                verbose_name='Maddələr siyahısı (RU)',
            ),
        ),
    ]
