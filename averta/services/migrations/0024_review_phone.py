from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0023_review_service_package'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='phone',
            field=models.CharField(
                blank=True,
                default='',
                max_length=40,
                verbose_name='Mobil nömrə',
            ),
        ),
    ]
