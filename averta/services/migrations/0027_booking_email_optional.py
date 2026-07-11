from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0026_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email'),
        ),
        migrations.AlterModelOptions(
            name='booking',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Sifariş (ana səhifə forması)',
                'verbose_name_plural': 'Sifarişlər (ana səhifə forması)',
            },
        ),
    ]
