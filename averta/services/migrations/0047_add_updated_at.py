import django.utils.timezone
from django.db import migrations, models


TIMESTAMP_MODELS = (
    'appealcontact',
    'blog',
    'booking',
    'faq',
    'media',
    'package',
    'partner',
    'review',
    'service',
)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0046_revert_package_price_from'),
    ]

    operations = [
        migrations.AddField(
            model_name=model_name,
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Yenilənmə tarixi',
            ),
        )
        for model_name in TIMESTAMP_MODELS
    ]
