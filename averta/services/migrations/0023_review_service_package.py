from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0022_alter_review_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='service',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reviews',
                to='services.service',
                verbose_name='Xidmət',
            ),
        ),
        migrations.AddField(
            model_name='review',
            name='package',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reviews',
                to='services.package',
                verbose_name='Paket',
            ),
        ),
    ]
