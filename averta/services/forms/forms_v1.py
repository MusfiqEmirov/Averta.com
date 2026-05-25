from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from services.models import AppealContact, Review


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
        max_length=120,
        strip=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('E-poçt ünvanınız'),
            'autocomplete': 'email',
        }),
        required=True,
        label=_('E-poçt'),
        max_length=254,
        strip=True,
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
        max_length=1000,
        strip=True,
    )
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True,
        initial=0,
    )

    class Meta:
        model = Review
        fields = ['name', 'email', 'message', 'rating']

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise ValidationError(_('Something went wrong. Please try again.'))
        return value

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating or rating < 1:
            raise ValidationError(_('Zəhmət olmasa ulduz reytinqi seçin.'))
        if rating > 5:
            raise ValidationError(_('Reytinq 1 ilə 5 arasında olmalıdır.'))
        return rating
