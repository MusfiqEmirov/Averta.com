import django.core.validators
from django.db import migrations, models

import services.models.review_models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0019_review_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='message',
            field=models.TextField(
                validators=[
                    django.core.validators.MaxLengthValidator(
                        services.models.review_models.REVIEW_MESSAGE_MAX_LENGTH
                    )
                ],
                verbose_name='Review',
            ),
        ),
    ]
