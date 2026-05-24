from django.db import migrations, models
from django.utils.text import slugify


def populate_blog_slugs(apps, schema_editor):
    Blog = apps.get_model('services', 'Blog')
    for blog in Blog.objects.all().order_by('id'):
        if blog.slug:
            continue
        base = slugify(blog.name_az) or f'blog-{blog.pk}'
        slug = base
        num = 1
        while Blog.objects.filter(slug=slug).exclude(pk=blog.pk).exists():
            slug = f'{base}-{num}'
            num += 1
        blog.slug = slug
        blog.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_blog_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='slug',
            field=models.SlugField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                unique=True,
                verbose_name='Slug',
            ),
        ),
        migrations.RunPython(populate_blog_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='blog',
            name='slug',
            field=models.SlugField(
                blank=True,
                db_index=True,
                max_length=255,
                unique=True,
                verbose_name='Slug',
            ),
        ),
    ]
