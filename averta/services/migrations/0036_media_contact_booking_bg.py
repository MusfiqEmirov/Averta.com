from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0035_remove_media_footer_contact_cta_bg'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_contact_booking_background_image',
            field=models.BooleanField(
                default=False,
                verbose_name='Elaqe sehifesi Sifaris et bolmesi fonu',
            ),
        ),
    ]
