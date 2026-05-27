from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0024_review_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appealcontact',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email'),
        ),
    ]

