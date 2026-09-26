from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0053_booking_arrival_date_package_show_arrival_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='value_one',
            field=models.CharField(
                blank=True,
                help_text='Məsələn: 25 və ya 90+. Ana səhifə və Haqqımızda səhifəsində sol tərəfdəki birinci rəqəm.',
                max_length=32,
                null=True,
                verbose_name='1-ci kart — böyük rəqəm',
            ),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='value_two',
            field=models.CharField(
                blank=True,
                help_text='Məsələn: 150 və ya 90+. İkinci statistika kartındakı rəqəm.',
                max_length=32,
                null=True,
                verbose_name='2-ci kart — böyük rəqəm',
            ),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='value_three',
            field=models.CharField(
                blank=True,
                help_text='Məsələn: 500 və ya 90+. Üçüncü statistika kartındakı rəqəm.',
                max_length=32,
                null=True,
                verbose_name='3-cü kart — böyük rəqəm',
            ),
        ),
        migrations.AlterField(
            model_name='statistic',
            name='value_four',
            field=models.CharField(
                blank=True,
                help_text='Məsələn: 1000 və ya 90+. Dördüncü statistika kartındakı rəqəm.',
                max_length=32,
                null=True,
                verbose_name='4-cü kart — böyük rəqəm',
            ),
        ),
    ]
