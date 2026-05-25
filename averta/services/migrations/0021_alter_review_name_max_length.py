from django.db import migrations, models

import services.models.review_models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0020_alter_review_message_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='name',
            field=models.CharField(
                max_length=services.models.review_models.REVIEW_NAME_MAX_LENGTH,
                verbose_name='Name',
            ),
        ),
    ]
