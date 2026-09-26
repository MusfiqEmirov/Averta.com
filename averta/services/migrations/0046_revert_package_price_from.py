import re
from decimal import Decimal, InvalidOperation

from django.db import migrations, models


def migrate_prices_to_decimal(apps, schema_editor):
    Package = apps.get_model('services', 'Package')
    for package in Package.objects.all().iterator():
        raw = (getattr(package, 'price_az', '') or '').strip().lower()
        package.price_from = any(x in raw for x in ('dan', 'dən', 'den'))
        match = re.search(r'[\d.]+', raw)
        if match:
            try:
                package.price = Decimal(match.group())
            except InvalidOperation:
                package.price = Decimal('0')
        else:
            package.price = Decimal('0')
        package.save(update_fields=['price', 'price_from'])


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0045_package_price_i18n'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='price',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=100,
                verbose_name='Qiymət',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='price_from',
            field=models.BooleanField(
                default=False,
                help_text='İşarələnərsə saytda qiymət «$909-dan», «€907-dən» kimi göstərilir.',
                verbose_name='Qiymətə «dan/dən» əlavə et',
            ),
        ),
        migrations.RunPython(migrate_prices_to_decimal, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='package',
            name='price_az',
        ),
        migrations.RemoveField(
            model_name='package',
            name='price_en',
        ),
        migrations.RemoveField(
            model_name='package',
            name='price_ru',
        ),
    ]
