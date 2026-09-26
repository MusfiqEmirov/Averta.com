from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0018_review_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_read',
            field=models.BooleanField(
                default=False,
                help_text='Rəyi oxuduqdan sonra işarələyin.',
                verbose_name='Oxunub?',
            ),
        ),
    ]
