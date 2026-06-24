from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0050_service_sort_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='show_date_from',
            field=models.BooleanField(
                default=True,
                help_text='İşarələnərsə sifariş formunda gediş tarixi sahəsi göstərilir.',
                verbose_name='Sifariş formunda gediş tarixi',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='show_date_to',
            field=models.BooleanField(
                default=True,
                help_text='İşarələnərsə sifariş formunda qayıdış (gəliş) tarixi sahəsi göstərilir.',
                verbose_name='Sifariş formunda qayıdış tarixi',
            ),
        ),
    ]
