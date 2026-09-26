from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0012_package_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='icon',
            field=models.CharField(
                choices=[
                    ('plane', '✈ Təyyarə'),
                    ('hike', '🥾 Yürüyüş'),
                    ('mountain', '⛰ Dağ'),
                    ('compass', '🧭 Kompas'),
                    ('beach', '🏖 Çimərlik'),
                    ('boat', '⛵ Gəmi'),
                    ('camera', '📷 Fototur'),
                    ('city', '🏙 Şəhər turu'),
                    ('car', '🚗 Avtomobil turu'),
                    ('tent', '⛺ Düşərgə'),
                ],
                default='plane',
                max_length=20,
                verbose_name='İkon',
                help_text='Kart üzərindəki dekorativ ikon.',
            ),
        ),
    ]
