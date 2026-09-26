from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_service_description_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='currency',
            field=models.CharField(
                choices=[('AZN', 'AZN (₼)'), ('USD', 'USD ($)'), ('EUR', 'EUR (€)')],
                default='AZN',
                max_length=3,
                verbose_name='Valyuta',
            ),
        ),
    ]
