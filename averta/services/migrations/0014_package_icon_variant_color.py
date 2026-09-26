from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_package_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='icon',
            new_name='icon_type',
        ),
        migrations.AddField(
            model_name='package',
            name='icon_variant',
            field=models.CharField(
                choices=[('1', 'Stil 1'), ('2', 'Stil 2'), ('3', 'Stil 3')],
                default='1',
                max_length=1,
                verbose_name='İkon stili',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='icon_color',
            field=models.CharField(
                choices=[
                    ('auto', 'Avtomatik'),
                    ('blue', 'Mavi'),
                    ('green', 'Yaşıl'),
                    ('purple', 'Bənövşəyi'),
                    ('orange', 'Narıncı'),
                    ('cyan', 'Firuzəyi'),
                    ('rose', 'Çəhrayı'),
                    ('slate', 'Boz'),
                    ('indigo', 'İndigo'),
                    ('amber', 'Kəhrəba'),
                    ('teal', 'Tünd yaşıl'),
                    ('crimson', 'Tünd qırmızı'),
                ],
                default='auto',
                max_length=20,
                verbose_name='Kart rəngi',
                help_text='Başlıq fonunun gradient rəngi.',
            ),
        ),
        migrations.AlterField(
            model_name='package',
            name='icon_type',
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
                verbose_name='İkon növü',
                help_text='Kart üzərindəki ikon kateqoriyası.',
            ),
        ),
    ]
