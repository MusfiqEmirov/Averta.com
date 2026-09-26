from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0038_statistic_nullable_fields'),
        ('services', '0039_alter_statistic_icon_four_alter_statistic_icon_one_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='date_from',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Başlama tarixi',
                help_text='Səyahətin başlama tarixi.',
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='date_to',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='Bitmə tarixi',
                help_text='Səyahətin bitmə tarixi.',
            ),
        ),
    ]
