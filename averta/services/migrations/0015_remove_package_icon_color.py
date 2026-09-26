from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0014_package_icon_variant_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='icon_color',
        ),
    ]
