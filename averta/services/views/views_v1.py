import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import F
from django.views import View

from services.models import Blog
from services.forms.forms_v1 import AppealContactForm, ReviewForm
from services.utils.send_email import send_appeal_contact_notification
from services.utils.queries import (
    get_language_from_request,
    get_home_page_data,
    get_service_list_data,
    get_background_image,
    get_about,
    serialize_about,
    get_partners,
    serialize_partner,
    get_contact,
    serialize_contact,
    get_statistics,
    get_blog_list_data,
    get_blog_by_slug,
    serialize_blog,
    get_other_blogs,
    get_page_motto,
    get_faqs,
    serialize_faq,
    get_service_by_slug,
    serialize_service,
    get_other_services,
)


class HomePageView(View):
    template_name = 'index.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        context['review_form'] = ReviewForm(lang=lang)
        context['review_feedback'] = request.session.pop('review_feedback', None)
        return render(request, self.template_name, context)

    def post(self, request):
        lang = get_language_from_request(request)

        if request.POST.get('form_type') != 'review':
            return redirect(reverse('services:home-page'))

        form = ReviewForm(request.POST, lang=lang)

        if form.is_valid():
            try:
                form.save()
                request.session['review_feedback'] = 'success'
            except Exception:
                logging.getLogger(__name__).exception('Review form save failed.')
                request.session['review_feedback'] = 'error'
            return redirect(reverse('services:home-page') + '#testimonial')

        # Validasiya xətası — modal yenidən açılır, sahə xətaları göstərilir
        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        context['review_form'] = form
        context['review_feedback'] = None
        return render(request, self.template_name, context)


class ServicePageView(View):
    template_name = 'services.html'

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_service_list_data(request, lang)
        context['background_image'] = get_background_image('service')
        context['language'] = lang
        context['active_nav'] = 'services'
        return render(request, self.template_name, context)


class ServiceDetailPageView(View):
    template_name = 'service-detail.html'

    def get(self, request, service_slug):
        lang = get_language_from_request(request)
        service = get_service_by_slug(service_slug)
        if not service:
            raise Http404(_('Service not found'))

        contact = get_contact(lang)
        context = {
            'service': serialize_service(service, lang),
            'other_services': get_other_services(service_slug, lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('service'),
            'page_motto': get_page_motto('service', lang),
            'active_nav': 'services',
        }
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
        page_heading = _('About us')

        context = {
            'about': serialize_about(about, lang) if about else None,
            'partners': [serialize_partner(p, lang) for p in partners],
            'contact': serialize_contact(contact, lang) if contact else None,
            'statistics': statistics,
            'language': lang,
            'background_image': get_background_image('about'),
            'page_heading': page_heading,
            'page_motto': get_page_motto('about', lang),
            'active_nav': 'about',
        }
        return render(request, self.template_name, context)


class ContactPageView(View):
    template_name = 'contact.html'

    def get(self, request):
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        form = AppealContactForm()
        page_heading = _('Contact')

        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
            'active_nav': 'contact',
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
                return redirect('services:contact-page')
            except Exception:
                logging.getLogger(__name__).exception('Contact form save failed.')
                messages.error(request, _('Something went wrong. Please try again.'))
        else:
            messages.error(request, _('Please correct the errors in the form.'))

        contact = get_contact(lang)
        page_heading = _('Contact')

        context = {
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
            'active_nav': 'contact',
        }
        return render(request, self.template_name, context)


class FAQPageView(View):
    template_name = 'faq.html'

    def get(self, request):
        lang = get_language_from_request(request)
        faqs = get_faqs(lang)
        contact = get_contact(lang)
        page_heading = _('Tez-tez verilən suallar')

        context = {
            'faqs': [serialize_faq(f, lang) for f in faqs],
            'contact': serialize_contact(contact, lang) if contact else None,
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
        context['active_nav'] = 'blog'
        return render(request, self.template_name, context)


class BlogDetailPageView(View):
    template_name = 'blog-detail.html'

    def get(self, request, blog_slug):
        lang = get_language_from_request(request)
        blog = get_blog_by_slug(blog_slug)
        if not blog:
            raise Http404(_('Blog post not found'))

        Blog.objects.filter(pk=blog.pk).update(view_count=F('view_count') + 1)
        blog.refresh_from_db()

        blog_data = serialize_blog(blog, lang)

        contact = get_contact(lang)
        context = {
            'blog': blog_data,
            'other_blogs': get_other_blogs(blog.pk, lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('blog'),
            'page_motto': get_page_motto('blog', lang),
            'active_nav': 'blog',
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
