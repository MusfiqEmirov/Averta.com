import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import F
from django.views import View

from projects.models import Blog
from projects.forms.forms_v1 import AppealContactForm
from projects.utils.send_email import send_appeal_contact_notification
from projects.utils.queries import (
    get_language_from_request,
    get_home_page_data,
    get_product_list_data,
    get_background_image,
    get_about,
    serialize_about,
    get_partners,
    serialize_partner,
    get_contact,
    serialize_contact,
    get_statistics,
    get_product_categories,
    serialize_product_category,
    get_blog_list_data,
    get_blog_by_id,
    serialize_blog,
    get_other_blogs,
    get_page_motto,
    get_faqs,
    serialize_faq,
)


class HomePageView(View):
    template_name = 'index.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_home_page_data(request, lang)
        context['language'] = lang
        return render(request, self.template_name, context)


class ProductPageView(View):
    template_name = 'products.html'

    def get(self, request, category_slug=None):
        lang = get_language_from_request(request)
        slug = category_slug or request.GET.get('slug')
        if not slug:
            return redirect('projects:home-page')
        if category_slug:
            request.GET = request.GET.copy()
            request.GET['slug'] = category_slug
        context = get_product_list_data(request, lang)
        context['background_image'] = get_background_image('product')
        context['language'] = lang
        return render(request, self.template_name, context)


class AboutPageView(View):
    template_name = 'about.html'

    def get(self, request):
        lang = get_language_from_request(request)
        is_active = request.GET.get('is_active', 'true').lower() == 'true'
        about = get_about(lang)
        partners = get_partners(lang=lang, is_active=is_active)
        contact = get_contact(lang)
        statistics = get_statistics(lang)
        categories = get_product_categories(lang)
        page_heading = _('About us')

        context = {
            'about': serialize_about(about, lang) if about else None,
            'partners': [serialize_partner(p, lang) for p in partners],
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': [serialize_product_category(c, lang) for c in categories],
            'statistics': statistics,
            'language': lang,
            'background_image': get_background_image('about'),
            'page_heading': page_heading,
            'page_motto': get_page_motto('about', lang),
        }
        return render(request, self.template_name, context)


class ContactPageView(View):
    template_name = 'contact.html'

    def get(self, request):
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        categories = get_product_categories(lang)
        form = AppealContactForm()
        page_heading = _('Contact')

        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': [serialize_product_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        lang = get_language_from_request(request)
        form = AppealContactForm(request.POST)

        if form.is_valid():
            try:
                appeal = form.save()
                send_appeal_contact_notification(appeal)
                messages.success(
                    request,
                    _('Thank you. We have received your message.'),
                )
                return redirect('projects:contact-page')
            except Exception:
                logging.getLogger(__name__).exception('Contact form save failed.')
                messages.error(request, _('Something went wrong. Please try again.'))
        else:
            messages.error(request, _('Please correct the errors in the form.'))

        contact = get_contact(lang)
        categories = get_product_categories(lang)
        page_heading = _('Contact')

        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'categories': [serialize_product_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
        }
        return render(request, self.template_name, context)


class FAQPageView(View):
    template_name = 'faq.html'

    def get(self, request):
        lang = get_language_from_request(request)
        faqs = get_faqs(lang)
        categories = get_product_categories(lang)
        page_heading = _('Tez-tez verilən suallar')

        context = {
            'faqs': [serialize_faq(f, lang) for f in faqs],
            'categories': [serialize_product_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('contact'),
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
        }
        return render(request, self.template_name, context)


class BlogPageView(View):
    template_name = 'blog.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_blog_list_data(request, lang)
        context['language'] = lang
        context['background_image'] = get_background_image('blog')
        categories = get_product_categories(lang)
        context['categories'] = [serialize_product_category(c, lang) for c in categories]
        return render(request, self.template_name, context)


class BlogDetailPageView(View):
    template_name = 'blog-detail.html'

    def get(self, request, blog_id):
        lang = get_language_from_request(request)
        blog = get_blog_by_id(blog_id)
        if not blog:
            raise Http404(_('Blog post not found'))

        Blog.objects.filter(pk=blog_id).update(view_count=F('view_count') + 1)
        blog.refresh_from_db()

        blog_data = serialize_blog(blog, lang)
        categories = get_product_categories(lang)

        context = {
            'blog': blog_data,
            'other_blogs': get_other_blogs(blog_id, lang),
            'language': lang,
            'categories': [serialize_product_category(c, lang) for c in categories],
            'background_image': get_background_image('blog'),
            'page_motto': get_page_motto('blog', lang),
        }
        return render(request, self.template_name, context)


class BlogViewCountsApiView(View):
    """Current view_count for one or more blog posts (JSON). Refreshes UI without full reload."""

    def get(self, request):
        raw = request.GET.get('ids', '')
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        id_list = []
        for p in parts[:50]:
            if p.isdigit():
                id_list.append(int(p))
        if not id_list:
            return JsonResponse({})
        rows = Blog.objects.filter(pk__in=id_list).values('id', 'view_count')
        return JsonResponse({str(r['id']): r['view_count'] for r in rows})
