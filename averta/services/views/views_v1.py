import logging

from django import forms
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import F
from django.views import View
from django.conf import settings

from services.models import Blog
from services.forms.forms_v1 import AppealContactForm, BookingForm, ReviewForm
from services.utils.send_email import send_appeal_contact_notification, send_booking_notification
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

def _is_ajax(request) -> bool:
    """True when browser asked for JSON (fetch/XHR)."""
    return (request.headers.get('X-Requested-With') or '').lower() == 'xmlhttprequest'

def _first_form_error_message(form) -> str:
    """
    Return the first useful error message from a Django form.
    Prefers non-field errors, then first field error.
    """
    try:
        nfe = form.non_field_errors()
        if nfe:
            return str(nfe[0])
    except Exception:
        pass
    try:
        for field in form.errors:
            errors = form.errors.get(field)
            if errors:
                return str(errors[0])
    except Exception:
        pass
    return ''


class HomePageView(View):
    template_name = 'index.html'

    @staticmethod
    def _compact_home_appeal_form(form: AppealContactForm) -> AppealContactForm:
        """Tweak AppealContactForm widgets for compact home section."""
        # Hide subject on home page (we set initial separately)
        if 'subject' in form.fields:
            form.fields['subject'].widget = forms.HiddenInput()

        # Smaller controls + tighter textarea
        for key in ('full_name', 'phone', 'email'):
            if key in form.fields:
                attrs = form.fields[key].widget.attrs
                attrs['class'] = 'form-control form-control-sm'
        if 'info' in form.fields:
            attrs = form.fields['info'].widget.attrs
            attrs['class'] = 'form-control form-control-sm'
            attrs['rows'] = 3

        return form

    def get(self, request):
        lang = get_language_from_request(request)
        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        # Turnstile (render + script) should work even if context processors are overridden
        context['turnstile_site_key'] = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
        context['turnstile_enabled'] = bool(
            context['turnstile_site_key']
            and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
        )
        context['review_form'] = ReviewForm(lang=lang)
        context['review_feedback'] = request.session.pop('review_feedback', None)
        context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
        context['booking_feedback'] = request.session.pop('booking_feedback', None)
        appeal_form = AppealContactForm(lang=lang, request=request)
        appeal_form.fields['subject'].initial = 'Ana səhifə'
        context['appeal_form'] = self._compact_home_appeal_form(appeal_form)
        context['appeal_feedback'] = request.session.pop('appeal_feedback', None)
        return render(request, self.template_name, context)

    def post(self, request):
        lang = get_language_from_request(request)
        form_type = request.POST.get('form_type')

        if form_type == 'booking':
            return self._handle_booking_post(request, lang)
        if form_type == 'review':
            return self._handle_review_post(request, lang)
        if form_type == 'appeal':
            return self._handle_appeal_post(request, lang)
        return redirect(reverse('services:home-page'))

    def _handle_appeal_post(self, request, lang):
        form = AppealContactForm(request.POST, lang=lang, request=request)
        # hide subject on home page, but still required
        self._compact_home_appeal_form(form)
        if form.is_valid():
            try:
                appeal = form.save()
                send_appeal_contact_notification(appeal)
                feedback = 'success'
            except Exception:
                logging.getLogger(__name__).exception('Home contact form save failed.')
                feedback = 'error'

            if _is_ajax(request):
                return JsonResponse(
                    {
                        'ok': feedback == 'success',
                        'message': (
                            _('Mesajınız qəbul olundu.')
                            if feedback == 'success'
                            else _('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
                        ),
                    },
                    status=200 if feedback == 'success' else 500,
                )

            context = get_home_page_data(request, lang)
            context['language'] = lang
            context['active_nav'] = 'home'
            context['turnstile_site_key'] = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
            context['turnstile_enabled'] = bool(
                context['turnstile_site_key']
                and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
            )
            context['review_form'] = ReviewForm(lang=lang)
            context['review_feedback'] = None
            context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
            context['booking_feedback'] = None
            appeal_form = AppealContactForm(lang=lang, request=request)
            appeal_form.fields['subject'].initial = 'Ana səhifə'
            context['appeal_form'] = self._compact_home_appeal_form(appeal_form)
            context['appeal_feedback'] = feedback
            return render(request, self.template_name, context)

        if _is_ajax(request):
            return JsonResponse(
                {
                    'ok': False,
                    'message': _first_form_error_message(form) or _('Zəhmət olmasa formadakı xətaları düzəldin.'),
                    'errors': form.errors.get_json_data(),
                },
                status=400,
            )

        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        context['review_form'] = ReviewForm(lang=lang)
        context['review_feedback'] = None
        context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
        context['booking_feedback'] = None
        context['appeal_form'] = form
        context['appeal_feedback'] = None
        return render(request, self.template_name, context)

    def _handle_booking_post(self, request, lang):
        prefix = 'modal' if request.POST.get('modal-booking_type') is not None else None
        form = BookingForm(request.POST, lang=lang, prefix=prefix)

        if form.is_valid():
            try:
                booking = form.save()
                send_booking_notification(booking)
                feedback = 'success'
            except Exception:
                logging.getLogger(__name__).exception('Booking form save failed.')
                feedback = 'error'

            if _is_ajax(request):
                return JsonResponse(
                    {
                        'ok': feedback == 'success',
                        'message': (
                            _('Sifarişiniz qəbul olundu. Tezliklə sizinlə əlaqə saxlayacağıq.')
                            if feedback == 'success'
                            else _('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
                        ),
                    },
                    status=200 if feedback == 'success' else 500,
                )

            context = get_home_page_data(request, lang)
            context['language'] = lang
            context['active_nav'] = 'home'
            context['turnstile_site_key'] = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
            context['turnstile_enabled'] = bool(
                context['turnstile_site_key']
                and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
            )
            context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
            context['booking_feedback'] = feedback
            context['review_form'] = ReviewForm(lang=lang)
            context['review_feedback'] = None
            appeal_form = AppealContactForm(lang=lang, request=request)
            appeal_form.fields['subject'].initial = 'Ana səhifə'
            context['appeal_form'] = self._compact_home_appeal_form(appeal_form)
            context['appeal_feedback'] = None
            return render(request, self.template_name, context)

        if _is_ajax(request):
            return JsonResponse(
                {
                    'ok': False,
                    'message': _first_form_error_message(form) or _('Zəhmət olmasa formadakı xətaları düzəldin.'),
                    'errors': form.errors.get_json_data(),
                },
                status=400,
            )

        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        context['booking_form'] = form
        context['booking_feedback'] = None
        context['review_form'] = ReviewForm(lang=lang)
        context['review_feedback'] = None
        return render(request, self.template_name, context)

    def _handle_review_post(self, request, lang):
        form = ReviewForm(request.POST, lang=lang)

        if form.is_valid():
            try:
                form.save()
                feedback = 'success'
            except Exception:
                logging.getLogger(__name__).exception('Review form save failed.')
                feedback = 'error'

            if _is_ajax(request):
                return JsonResponse(
                    {
                        'ok': feedback == 'success',
                        'message': (
                            _('Rəyiniz qəbul edildi. Təsdiqdən sonra saytda görünəcək.')
                            if feedback == 'success'
                            else _('Rəyiniz göndərilmədi. Zəhmət olmasa yenidən cəhd edin.')
                        ),
                    },
                    status=200 if feedback == 'success' else 500,
                )

            context = get_home_page_data(request, lang)
            context['language'] = lang
            context['active_nav'] = 'home'
            context['turnstile_site_key'] = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
            context['turnstile_enabled'] = bool(
                context['turnstile_site_key']
                and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
            )
            context['review_form'] = ReviewForm(lang=lang)
            context['review_feedback'] = feedback
            context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
            context['booking_feedback'] = None
            appeal_form = AppealContactForm(lang=lang, request=request)
            appeal_form.fields['subject'].initial = 'Ana səhifə'
            context['appeal_form'] = self._compact_home_appeal_form(appeal_form)
            context['appeal_feedback'] = None
            return render(request, self.template_name, context)

        if _is_ajax(request):
            return JsonResponse(
                {
                    'ok': False,
                    'message': _first_form_error_message(form) or _('Zəhmət olmasa formadakı xətaları düzəldin.'),
                    'errors': form.errors.get_json_data(),
                },
                status=400,
            )

        context = get_home_page_data(request, lang)
        context['language'] = lang
        context['active_nav'] = 'home'
        context['review_form'] = form
        context['review_feedback'] = None
        context['booking_form'] = BookingForm(lang=lang, initial={'booking_type': 'package'})
        context['booking_feedback'] = None
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
        service_data = serialize_service(service, lang)
        context = {
            'service': service_data,
            'other_services': get_other_services(service_slug, lang),
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('service'),
            'page_motto': get_page_motto('service', lang),
            'active_nav': 'services',
            'og_image': (
                request.build_absolute_uri(service_data['cover_image'])
                if service_data.get('cover_image') else None
            ),
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

    @staticmethod
    def _t(request, lang: str, *, az: str, en: str, ru: str) -> str:
        """Small helper to pick a message without requiring locale catalogs."""
        if lang == 'en':
            return en
        if lang == 'ru':
            return ru
        return az

    def get(self, request):
        lang = get_language_from_request(request)
        contact = get_contact(lang)
        form = AppealContactForm(lang=lang, request=request)
        page_heading = _('Contact')

        context = self._contact_page_context(
            lang,
            contact,
            form=form,
            page_heading=page_heading,
        )
        return render(request, self.template_name, context)

    def post(self, request):
        lang = get_language_from_request(request)
        form = AppealContactForm(request.POST, lang=lang, request=request)

        if form.is_valid():
            try:
                appeal = form.save()
                send_appeal_contact_notification(appeal)
                if _is_ajax(request):
                    return JsonResponse(
                        {
                            'ok': True,
                            'message': self._t(
                                request,
                                lang,
                                az='Təşəkkür edirik. Mesajınız qəbul olundu.',
                                en='Thank you. We have received your message.',
                                ru='Спасибо. Мы получили ваше сообщение.',
                            ),
                        },
                        status=200,
                    )
                messages.success(
                    request,
                    self._t(
                        request,
                        lang,
                        az='Təşəkkür edirik. Mesajınız qəbul olundu.',
                        en='Thank you. We have received your message.',
                        ru='Спасибо. Мы получили ваше сообщение.',
                    ),
                )
                return redirect('services:contact-page')
            except Exception:
                logging.getLogger(__name__).exception('Contact form save failed.')
                if _is_ajax(request):
                    return JsonResponse(
                        {
                            'ok': False,
                            'message': self._t(
                                request,
                                lang,
                                az='Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.',
                                en='Something went wrong. Please try again.',
                                ru='Произошла ошибка. Пожалуйста, попробуйте ещё раз.',
                            ),
                        },
                        status=500,
                    )
                messages.error(
                    request,
                    self._t(
                        request,
                        lang,
                        az='Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.',
                        en='Something went wrong. Please try again.',
                        ru='Произошла ошибка. Пожалуйста, попробуйте ещё раз.',
                    ),
                )
        else:
            if _is_ajax(request):
                return JsonResponse(
                    {
                        'ok': False,
                        'message': self._t(
                            request,
                            lang,
                            az='Zəhmət olmasa formadakı xətaları düzəldin.',
                            en='Please correct the errors in the form.',
                            ru='Пожалуйста, исправьте ошибки в форме.',
                        ),
                        'errors': form.errors.get_json_data(),
                    },
                    status=400,
                )
            messages.error(
                request,
                self._t(
                    request,
                    lang,
                    az='Zəhmət olmasa formadakı xətaları düzəldin.',
                    en='Please correct the errors in the form.',
                    ru='Пожалуйста, исправьте ошибки в форме.',
                ),
            )

        contact = get_contact(lang)
        page_heading = _('Contact')

        context = self._contact_page_context(
            lang,
            contact,
            form=form,
            page_heading=page_heading,
        )
        return render(request, self.template_name, context)

    def _contact_page_context(
        self,
        lang,
        contact,
        *,
        form,
        page_heading,
    ):
        turnstile_site_key = (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
        return {
            'contact': serialize_contact(contact, lang) if contact else None,
            'language': lang,
            'background_image': get_background_image('contact'),
            'form': form,
            'page_heading': page_heading,
            'page_motto': get_page_motto('contact', lang),
            'active_nav': 'contact',
            # Ensure widget/script render reliably
            'turnstile_site_key': turnstile_site_key,
            'turnstile_enabled': bool(
                turnstile_site_key
                and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
            ),
        }


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
            'og_image': (
                request.build_absolute_uri(blog_data['image'])
                if blog_data.get('image') else None
            ),
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
