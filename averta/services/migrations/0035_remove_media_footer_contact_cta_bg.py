from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0034_alter_media_options_alter_media_about_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='is_footer_contact_cta_background_image',
        ),
    ]
