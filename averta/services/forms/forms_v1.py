from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from services.models import AppealContact, Booking, Package, Review, Service
from services.models.review_models import REVIEW_MESSAGE_MAX_LENGTH, REVIEW_NAME_MAX_LENGTH
from services.utils import normalize_az_phone
from services.utils.queries import get_localized_field_name, get_packages, get_services
from services.utils.turnstile import verify_turnstile_response, is_turnstile_configured


class TurnstileMixin:
    """
    Cloudflare Turnstile checkbox validation.
    Expects the widget to post `cf-turnstile-response`.
    """

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._turnstile_request = request
        # NOTE: This mixin is not a Django Form subclass, so declaring a Field
        # as a class attribute would not be picked up by Django's form metaclass.
        # We must inject it into `self.fields` so templates render a BoundField.
        self.fields.setdefault(
            'turnstile',
            forms.CharField(required=False, widget=forms.HiddenInput(), label=''),
        )

    def _turnstile_is_enabled(self) -> bool:
        return is_turnstile_configured()

    def _turnstile_verify(self) -> bool:
        if not self._turnstile_is_enabled():
            return True

        token = (self.data.get('cf-turnstile-response') or '').strip()
        if not token:
            self.add_error('turnstile', _('Please verify that you are human.'))
            return False

        remote_ip = None
        req = getattr(self, '_turnstile_request', None)
        if req is not None:
            remote_ip = req.META.get('REMOTE_ADDR')

        ok = verify_turnstile_response(token, remote_ip=remote_ip)
        if not ok:
            self.add_error('turnstile', _('Captcha verification failed. Please try again.'))
        return ok


class AppealContactForm(TurnstileMixin, forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Your full name')
        }),
        required=True,
        label=_('Full name')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Email address')
        }),
        required=False,
        label=_('Email address')
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Mobile number'),
            'inputmode': 'tel',
            'autocomplete': 'tel',
        }),
        label=_('Mobile number'),
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Subject')
        }),
        required=True,
        label=_('Subject'),
        max_length=250
    )
    info = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-lg contact-message-field',
            'rows': 8,
            'placeholder': _('Your message')
        }),
        required=True,
        label=_('Your message'),
        max_length=500
    )

    class Meta:
        model = AppealContact
        fields = [
            'full_name',
            'email',
            'phone',
            'subject',
            'info'
        ]

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip()
        phone = (cleaned_data.get('phone') or '').strip()

        if not email and not phone:
            raise ValidationError(_('E-poçt və ya mobil nömrədən ən azı biri mütləqdir.'))
        self._turnstile_verify()
        return cleaned_data

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        return email

    def clean_phone(self):
        raw = (self.cleaned_data.get('phone') or '').strip()
        if not raw:
            return ''
        # Accept broader phone formats (international / different spacing).
        # Normalize Azerbaijan numbers if possible, otherwise keep user's input.
        normalized = normalize_az_phone(raw)
        return normalized or raw

    def __init__(self, *args, lang='az', **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        ui = {
            'az': {
                'full_name_label': 'Ad soyad *',
                'full_name_ph': 'Ad soyad *',
                'email_label': 'E-poçt',
                'email_ph': 'E-poçt (istəyə görə)',
                'phone_label': 'Mobil nömrə *',
                'phone_ph': 'Mobil nömrə *',
                'info_label': 'Mesajınız *',
                'info_ph': 'Mesajınız *',
            },
            'en': {
                'full_name_label': 'Full name *',
                'full_name_ph': 'Full name *',
                'email_label': 'Email',
                'email_ph': 'Email (optional)',
                'phone_label': 'Mobile number *',
                'phone_ph': 'Mobile number *',
                'info_label': 'Your message *',
                'info_ph': 'Your message *',
            },
            'ru': {
                'full_name_label': 'Имя и фамилия *',
                'full_name_ph': 'Имя и фамилия *',
                'email_label': 'Эл. почта',
                'email_ph': 'Эл. почта (необязательно)',
                'phone_label': 'Мобильный номер *',
                'phone_ph': 'Мобильный номер *',
                'info_label': 'Ваше сообщение *',
                'info_ph': 'Ваше сообщение *',
            },
        }.get(lang)

        if ui:
            self.fields['full_name'].label = ui['full_name_label']
            self.fields['full_name'].widget.attrs['placeholder'] = ui['full_name_ph']
            self.fields['email'].label = ui['email_label']
            self.fields['email'].widget.attrs['placeholder'] = ui['email_ph']
            self.fields['phone'].label = ui['phone_label']
            self.fields['phone'].widget.attrs['placeholder'] = ui['phone_ph']
            self.fields['info'].label = ui['info_label']
            self.fields['info'].widget.attrs['placeholder'] = ui['info_ph']


class BookingForm(forms.ModelForm):
    """Ana səhifə hero sifariş formu."""

    BOOKING_TYPE_SERVICE = 'service'
    BOOKING_TYPE_PACKAGE = 'package'
    BOOKING_TYPE_CHOICES = (
        (BOOKING_TYPE_SERVICE, _('Xidmət')),
        (BOOKING_TYPE_PACKAGE, _('Paket')),
    )

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    booking_type = forms.ChoiceField(
        choices=BOOKING_TYPE_CHOICES,
        initial=BOOKING_TYPE_PACKAGE,
        widget=forms.HiddenInput(),
    )
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'hero-booking__input',
            'placeholder': _('Ad soyad *'),
            'autocomplete': 'name',
        }),
        required=True,
        label=_('Ad soyad'),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'hero-booking__input',
            'placeholder': _('E-poçt (istəyə görə)'),
            'autocomplete': 'email',
        }),
        required=False,
        label=_('E-poçt'),
    )
    phone = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'hero-booking__input',
            'placeholder': _('Mobil nömrə *'),
            'inputmode': 'tel',
            'autocomplete': 'tel',
        }),
        label=_('Mobil nömrə'),
    )
    note = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'hero-booking__input',
            'placeholder': _('Qeyd (istəyə görə)'),
            'maxlength': '200',
        }),
        required=False,
        label=_('Qeyd'),
        max_length=200,
    )
    adults_count = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=1,
        widget=forms.HiddenInput(attrs={'class': 'hero-booking__count-input', 'data-counter': 'adults'}),
        label=_('Böyük sayı'),
    )
    children_count = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=0,
        widget=forms.HiddenInput(attrs={'class': 'hero-booking__count-input', 'data-counter': 'children'}),
        label=_('Uşaq sayı'),
    )
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hb-check'}),
        label=_('Xidmətlər'),
    )
    packages = forms.ModelMultipleChoiceField(
        queryset=Package.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hb-check'}),
        label=_('Paketlər'),
    )

    class Meta:
        model = Booking
        fields = [
            'full_name',
            'email',
            'phone',
            'note',
            'adults_count',
            'children_count',
        ]

    def __init__(self, *args, lang='az', **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        ui = {
            'az': {
                'full_name_label': 'Ad soyad',
                'full_name_ph': 'Ad soyad *',
                'email_label': 'E-poçt',
                'email_ph': 'E-poçt (istəyə görə)',
                'phone_label': 'Mobil nömrə',
                'phone_ph': 'Mobil nömrə *',
                'note_label': 'Qeyd',
                'note_ph': 'Qeyd (istəyə görə)',
                'svc': 'Xidmət',
                'pkg': 'Paket',
            },
            'en': {
                'full_name_label': 'Full name',
                'full_name_ph': 'Full name *',
                'email_label': 'Email',
                'email_ph': 'Email (optional)',
                'phone_label': 'Mobile number',
                'phone_ph': 'Mobile number *',
                'note_label': 'Note',
                'note_ph': 'Note (optional)',
                'svc': 'Service',
                'pkg': 'Package',
            },
            'ru': {
                'full_name_label': 'Имя и фамилия',
                'full_name_ph': 'Имя и фамилия *',
                'email_label': 'Эл. почта',
                'email_ph': 'Эл. почта (необязательно)',
                'phone_label': 'Мобильный номер',
                'phone_ph': 'Мобильный номер *',
                'note_label': 'Комментарий',
                'note_ph': 'Комментарий (необязательно)',
                'svc': 'Услуга',
                'pkg': 'Пакет',
            },
        }.get(lang)

        if ui:
            self.fields['full_name'].label = ui['full_name_label']
            self.fields['full_name'].widget.attrs['placeholder'] = ui['full_name_ph']
            self.fields['email'].label = ui['email_label']
            self.fields['email'].widget.attrs['placeholder'] = ui['email_ph']
            self.fields['phone'].label = ui['phone_label']
            self.fields['phone'].widget.attrs['placeholder'] = ui['phone_ph']
            self.fields['note'].label = ui['note_label']
            self.fields['note'].widget.attrs['placeholder'] = ui['note_ph']
            self.fields['services'].label = ui['svc']
            self.fields['packages'].label = ui['pkg']
        name_field = get_localized_field_name('name', lang)

        def label_instance(obj):
            return getattr(obj, name_field, None) or getattr(obj, 'name_az', str(obj))

        service_qs = get_services(lang=lang, is_active=True)
        package_qs = get_packages(lang=lang, is_active=True)
        self.fields['services'].queryset = service_qs
        self.fields['packages'].queryset = package_qs
        self.fields['services'].label_from_instance = label_instance
        self.fields['packages'].label_from_instance = label_instance

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean(self):
        cleaned_data = super().clean()
        booking_type = cleaned_data.get('booking_type') or self.BOOKING_TYPE_PACKAGE
        services = cleaned_data.get('services')
        packages = cleaned_data.get('packages')

        if booking_type == self.BOOKING_TYPE_PACKAGE:
            if not packages:
                self.add_error('packages', _('Ən azı bir paket seçin.'))
            cleaned_data['services'] = []
        else:
            if not services:
                self.add_error('services', _('Ən azı bir xidmət seçin.'))
            cleaned_data['packages'] = []
        return cleaned_data

    def clean_email(self):
        return (self.cleaned_data.get('email') or '').strip().lower()

    def clean_phone(self):
        raw = (self.cleaned_data.get('phone') or '').strip()
        if not raw:
            raise ValidationError(_('Mobil nömrə mütləqdir.'))
        normalized = normalize_az_phone(raw)
        return normalized or raw

    def save(self, commit=True):
        booking_type = self.cleaned_data.get('booking_type') or self.BOOKING_TYPE_PACKAGE
        services = self.cleaned_data.get('services')
        packages = self.cleaned_data.get('packages')

        instance = super().save(commit=False)
        if commit:
            instance.save()
            if booking_type == self.BOOKING_TYPE_PACKAGE:
                instance.services.clear()
                instance.packages.set(packages or [])
            else:
                instance.packages.clear()
                instance.services.set(services or [])
        return instance


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'


class ReviewForm(forms.ModelForm):
    """Müştəri rəy formu — honeypot spam qoruması ilə."""

    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='',
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Adınız'),
            'autocomplete': 'name',
        }),
        required=True,
        label=_('Ad'),
        min_length=2,
        max_length=REVIEW_NAME_MAX_LENGTH,
        strip=True,
    )
    phone = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mobil nömrə (məs: 050 123 45 67)'),
            'inputmode': 'tel',
            'autocomplete': 'tel',
            'id': 'reviewPhone',
        }),
        label=_('Mobil nömrə'),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Rəyiniz'),
        }),
        required=True,
        label=_('Rəy'),
        min_length=5,
        max_length=REVIEW_MESSAGE_MAX_LENGTH,
        strip=True,
    )
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
        initial=0,
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        empty_label=_('Xidmət seçin'),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'reviewService'}),
        label=_('Xidmət'),
    )
    package = forms.ModelChoiceField(
        queryset=Package.objects.none(),
        required=False,
        empty_label=_('Paket seçin'),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'reviewPackage'}),
        label=_('Paket'),
    )

    class Meta:
        model = Review
        fields = ['name', 'phone', 'message', 'rating', 'service', 'package']

    def __init__(self, *args, lang='az', **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        ui = {
            'az': {
                'name_label': 'Ad',
                'name_ph': 'Adınız',
                'phone_label': 'Mobil nömrə',
                'phone_ph': 'Mobil nömrə (məs: 050 123 45 67)',
                'msg_label': 'Rəy',
                'msg_ph': 'Rəyiniz',
                'svc_label': 'Xidmət',
                'svc_empty': 'Xidmət seçin',
                'pkg_label': 'Paket',
                'pkg_empty': 'Paket seçin',
            },
            'en': {
                'name_label': 'Name',
                'name_ph': 'Your name',
                'phone_label': 'Mobile number',
                'phone_ph': 'Mobile number (e.g. +994 50 123 45 67)',
                'msg_label': 'Review',
                'msg_ph': 'Your review',
                'svc_label': 'Service',
                'svc_empty': 'Select a service',
                'pkg_label': 'Package',
                'pkg_empty': 'Select a package',
            },
            'ru': {
                'name_label': 'Имя',
                'name_ph': 'Ваше имя',
                'phone_label': 'Мобильный номер',
                'phone_ph': 'Мобильный номер (пример: +994 50 123 45 67)',
                'msg_label': 'Отзыв',
                'msg_ph': 'Ваш отзыв',
                'svc_label': 'Услуга',
                'svc_empty': 'Выберите услугу',
                'pkg_label': 'Пакет',
                'pkg_empty': 'Выберите пакет',
            },
        }.get(lang)

        if ui:
            self.fields['name'].label = ui['name_label']
            self.fields['name'].widget.attrs['placeholder'] = ui['name_ph']
            self.fields['phone'].label = ui['phone_label']
            self.fields['phone'].widget.attrs['placeholder'] = ui['phone_ph']
            self.fields['message'].label = ui['msg_label']
            self.fields['message'].widget.attrs['placeholder'] = ui['msg_ph']
            self.fields['service'].label = ui['svc_label']
            self.fields['service'].empty_label = ui['svc_empty']
            self.fields['package'].label = ui['pkg_label']
            self.fields['package'].empty_label = ui['pkg_empty']
        name_field = get_localized_field_name('name', lang)

        def label_instance(obj):
            return getattr(obj, name_field, None) or getattr(obj, 'name_az', str(obj))

        service_qs = get_services(lang=lang, is_active=True)
        package_qs = get_packages(lang=lang, is_active=True)
        self.fields['service'].queryset = service_qs
        self.fields['package'].queryset = package_qs
        self.fields['service'].label_from_instance = label_instance
        self.fields['package'].label_from_instance = label_instance

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        package = cleaned_data.get('package')
        if service and package:
            raise ValidationError(_('Yalnız xidmət və ya paket seçin.'))
        if not service and not package:
            raise ValidationError(_('Xidmət və ya paket seçin.'))
        phone = (cleaned_data.get('phone') or '').strip()
        if not phone:
            raise ValidationError(_('Mobil nömrə mütləqdir.'))
        if not Booking.objects.filter(phone=phone, is_customer=True, is_deleted=False).exists():
            not_customer_msg = {
                'az': 'Rəy yazmaq üçün müştərimiz olmalısınız. Zəhmət olmasa əvvəlcə sifariş verin.',
                'en': 'You must be our customer to leave a review. Please place a booking first.',
                'ru': 'Чтобы оставить отзыв, вы должны быть нашим клиентом. Сначала оформите заказ.',
            }.get(getattr(self, 'lang', 'az'), 'Rəy yazmaq üçün müştərimiz olmalısınız.')
            raise ValidationError(not_customer_msg)
        return cleaned_data

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean_phone(self):
        raw = (self.cleaned_data.get('phone') or '').strip()
        if not raw:
            raise ValidationError(_('Mobil nömrə mütləqdir.'))
        normalized = normalize_az_phone(raw)
        return normalized or raw

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or rating < 1:
            raise ValidationError(_('Zəhmət olmasa ulduz reytinqi seçin.'))
        if rating > 5:
            raise ValidationError(_('Reytinq 1 ilə 5 arasında olmalıdır.'))
        return rating
