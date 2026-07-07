from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from services.models import Blog, Service


class AvertaSitemap(Sitemap):
    protocol = 'https'

    def get_domain(self, site=None):
        domain = getattr(settings, 'SITE_DOMAIN', 'www.avertatravel.com')
        return domain.replace('https://', '').replace('http://', '').strip('/')


class StaticViewSitemap(AvertaSitemap):
    def items(self):
        return [
            'services:home-page',
            'services:service-page',
            'services:about-page',
            'services:blog-page',
            'services:contact-page',
            'services:faq-page',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        priorities = {
            'services:home-page': 1.0,
            'services:service-page': 0.9,
            'services:about-page': 0.8,
            'services:blog-page': 0.8,
            'services:contact-page': 0.8,
            'services:faq-page': 0.6,
        }
        return priorities.get(item, 0.8)

    def changefreq(self, item):
        freqs = {
            'services:home-page': 'daily',
            'services:blog-page': 'weekly',
            'services:contact-page': 'monthly',
        }
        return freqs.get(item, 'weekly')


class BlogSitemap(AvertaSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse('services:blog-detail', kwargs={'blog_slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at


class ServiceSitemap(AvertaSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('services:service-detail', kwargs={'service_slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at
