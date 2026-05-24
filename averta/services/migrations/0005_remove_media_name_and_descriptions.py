from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_remove_package_page_background_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='name_az',
        ),
        migrations.RemoveField(
            model_name='media',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='media',
            name='name_ru',
        ),
        migrations.RemoveField(
            model_name='media',
            name='short_description_az',
        ),
        migrations.RemoveField(
            model_name='media',
            name='short_description_en',
        ),
        migrations.RemoveField(
            model_name='media',
            name='short_description_ru',
        ),
    ]
