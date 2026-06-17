from django.db import migrations, models


def set_initial_sort_order(apps, schema_editor):
    """Mövcud sıranı saxla: indiki görünüş (-created_at) → 0, 1, 2, …"""
    Service = apps.get_model('services', 'Service')
    for index, service in enumerate(
        Service.objects.order_by('-created_at', '-id').iterator()
    ):
        Service.objects.filter(pk=service.pk).update(sort_order=index)


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0049_alter_appealcontact_updated_at_alter_blog_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='sort_order',
            field=models.PositiveIntegerField(
                db_index=True,
                default=0,
                help_text='0 = ilk (sayt, admin, menyu dropdown). 1 = sonrakı və s.',
                verbose_name='Sıra',
            ),
        ),
        migrations.RunPython(set_initial_sort_order, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name='service',
            options={
                'ordering': ('sort_order', 'id'),
                'verbose_name': 'Xidmət',
                'verbose_name_plural': 'Xidmətlər',
            },
        ),
    ]
