from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    Booking = apps.get_model('services', 'Booking')
    for booking in Booking.objects.all():
        service_id = getattr(booking, 'service_id', None)
        package_id = getattr(booking, 'package_id', None)
        if service_id:
            booking.services.add(service_id)
        if package_id:
            booking.packages.add(package_id)


def fill_empty_phones(apps, schema_editor):
    Booking = apps.get_model('services', 'Booking')
    Booking.objects.filter(phone='').update(phone='0000000000')


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_booking_email_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='services',
            field=models.ManyToManyField(
                blank=True,
                related_name='bookings',
                to='services.service',
                verbose_name='Xidmətlər',
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='packages',
            field=models.ManyToManyField(
                blank=True,
                related_name='bookings',
                to='services.package',
                verbose_name='Paketlər',
            ),
        ),
        migrations.RunPython(copy_fk_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='booking',
            name='service',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='package',
        ),
        migrations.RunPython(fill_empty_phones, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='phone',
            field=models.CharField(max_length=40, verbose_name='Mobil nömrə'),
        ),
    ]
