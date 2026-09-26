from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0032_media_footer_contact_cta_bg'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_home_contact_background_image',
            field=models.BooleanField(default=False, verbose_name='Ana sehife Elaqe bolmesi fon sekli'),
        ),
    ]
