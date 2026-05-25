from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from services.models import AppealContact, Package, Review, Service
from services.models.review_models import REVIEW_MESSAGE_MAX_LENGTH, REVIEW_NAME_MAX_LENGTH
from services.utils import normalize_az_phone
from services.utils.queries import get_localized_field_name, get_packages, get_services


class AppealContactForm(forms.ModelForm):
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
        required=True,
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
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('E-poçt ünvanınız'),
            'autocomplete': 'email',
            'id': 'reviewEmail',
        }),
        required=False,
        label=_('E-poçt'),
        max_length=254,
    )
    phone = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mobil nömrə'),
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
        fields = ['name', 'email', 'phone', 'message', 'rating', 'service', 'package']

    def __init__(self, *args, lang='az', **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
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

        email = (cleaned_data.get('email') or '').strip()
        phone = (cleaned_data.get('phone') or '').strip()
        if not email and not phone:
            raise ValidationError(_('E-poçt və ya mobil nömrədən ən azı biri mütləqdir.'))
        return cleaned_data

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        return email

    def clean_phone(self):
        raw = (self.cleaned_data.get('phone') or '').strip()
        if not raw:
            return ''
        normalized = normalize_az_phone(raw)
        if not normalized:
            raise ValidationError(_('Düzgün Azərbaycan mobil nömrəsi daxil edin.'))
        return normalized

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or rating < 1:
            raise ValidationError(_('Zəhmət olmasa ulduz reytinqi seçin.'))
        if rating > 5:
            raise ValidationError(_('Reytinq 1 ilə 5 arasında olmalıdır.'))
        return rating
