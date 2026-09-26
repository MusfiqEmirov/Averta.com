from django.db import migrations, models


def set_initial_sort_order(apps, schema_editor):
    """Mövcud sıranı saxla: indiki görünüş (-created_at) → 0, 1, 2, …"""
    Package = apps.get_model('services', 'Package')
    for index, package in enumerate(
        Package.objects.order_by('-created_at', '-id').iterator()
    ):
        Package.objects.filter(pk=package.pk).update(sort_order=index)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0051_package_booking_date_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='sort_order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                help_text='0 = ilk (sayt, admin siyahısı). 1 = sonrakı və s.',
                verbose_name='Sıra',
            ),
        ),
        migrations.RunPython(set_initial_sort_order, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='package',
            options={
                'ordering': ('sort_order', 'id'),
                'verbose_name': 'Paket',
                'verbose_name_plural': 'Paketlər',
            },
        ),
    ]
