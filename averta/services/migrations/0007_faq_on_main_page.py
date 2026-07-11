from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_statistic_icons'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='on_main_page',
            field=models.BooleanField(
                default=False,
                help_text='Yalnız işarələnən suallar ana səhifə FAQ blokunda görünür (ən çox 6).',
                verbose_name='Ana səhifədə göstərilsin?',
            ),
        ),
    ]
