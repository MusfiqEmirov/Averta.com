from django.core.validators import MaxLengthValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_service_bullet_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='description_az',
            field=models.TextField(
                validators=[MaxLengthValidator(5000)],
                verbose_name='Xidmət haqqında (AZ)',
            ),
        ),
        migrations.AlterField(
            model_name='service',
            name='description_en',
            field=models.TextField(
                blank=True,
                null=True,
                validators=[MaxLengthValidator(5000)],
                verbose_name='Xidmət haqqında (EN)',
            ),
        ),
        migrations.AlterField(
            model_name='service',
            name='description_ru',
            field=models.TextField(
                blank=True,
                null=True,
                validators=[MaxLengthValidator(5000)],
                verbose_name='Xidmət haqqında (RU)',
            ),
        ),
    ]
