from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0043_package_image_price_from'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='price_from',
        ),
        migrations.AlterField(
            model_name='package',
            name='price',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Məs: 909-dan. Seçilmiş valyutanın işarəsi avtomatik əlavə olunur (₼, $, €).',
                max_length=50,
                verbose_name='Qiymət',
            ),
        ),
    ]
