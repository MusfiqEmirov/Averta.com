from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0044_package_price_char_remove_price_from'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='price',
            new_name='price_az',
        ),
        migrations.AddField(
            model_name='package',
            name='price_en',
            field=models.CharField(
                blank=True,
                help_text='Məs: from $909',
                max_length=50,
                null=True,
                verbose_name='Qiymət (EN)',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='price_ru',
            field=models.CharField(
                blank=True,
                help_text='Məs: от €907',
                max_length=50,
                null=True,
                verbose_name='Qiymət (RU)',
            ),
        ),
        migrations.AlterField(
            model_name='package',
            name='price_az',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Məs: 909-dan. Seçilmiş valyutanın işarəsi avtomatik əlavə olunur (₼, $, €).',
                max_length=50,
                verbose_name='Qiymət (AZ)',
            ),
        ),
    ]
