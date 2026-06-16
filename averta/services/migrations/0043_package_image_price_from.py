from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0042_alter_booking_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Paket kartının yuxarı hissəsində göstərilir.',
                null=True,
                upload_to='images/packages/',
                verbose_name='Şəkil',
            ),
        ),
        migrations.AddField(
            model_name='package',
            name='price_from',
            field=models.BooleanField(
                default=False,
                help_text='İşarələnərsə saytda qiymət «60 manatdan», «33 dollardan» kimi göstərilir.',
                verbose_name='Qiymətə «dan/dən» əlavə et',
            ),
        ),
    ]
