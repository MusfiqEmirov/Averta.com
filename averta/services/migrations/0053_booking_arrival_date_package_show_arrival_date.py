from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0052_package_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='arrival_date',
            field=models.DateField(
                blank=True,
                help_text='Səyahətin gəliş tarixi.',
                null=True,
                verbose_name='Gəliş tarixi',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='show_arrival_date',
            field=models.BooleanField(
                default=False,
                help_text='İşarələnərsə sifariş formunda gəliş tarixi sahəsi göstərilir.',
                verbose_name='Sifariş formunda gəliş tarixi',
            ),
        ),
    ]
