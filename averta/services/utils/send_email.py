import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.formats import date_format

logger = logging.getLogger(__name__)


def format_appeal_contact_message(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone = instance.phone.strip() if instance.phone else '—'

    return (
        'Yeni əlaqə formu müraciəti\n'
        '────────────────────────────\n\n'
        f'Ad soyad:     {instance.full_name}\n'
        f'Email:        {instance.email}\n'
        f'Mobil nömrə:  {phone}\n'
        f'Mövzu:        {instance.subject}\n\n'
        'Mesaj:\n'
        f'{instance.info}\n\n'
        '────────────────────────────\n'
        f'Göndərilmə tarixi: {created_label}'
    )


def send_appeal_contact_notification(instance):
    try:
        subject = f'Yeni əlaqə müraciəti: {instance.subject}'
        message = format_appeal_contact_message(instance)
        recipient = settings.EMAIL_HOST_USER
        if not recipient:
            logger.warning('Contact form email skipped: EMAIL_HOST_USER is not set.')
            return
        send_mail_func(recipient, subject, message)
    except Exception:
        logger.exception('Contact form notification email failed.')


def format_booking_message(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone = instance.phone.strip() if instance.phone else '—'
    email = instance.email.strip() if instance.email else '—'
    service_labels = [str(s) for s in instance.services.all()]
    package_labels = [str(p) for p in instance.packages.all()]
    targets = service_labels + package_labels
    target_label = ', '.join(targets) if targets else '—'

    return (
        'Yeni sifariş (ana səhifə forması)\n'
        '────────────────────────────\n\n'
        f'Ad soyad:     {instance.full_name}\n'
        f'Email:        {email}\n'
        f'Mobil nömrə:  {phone}\n'
        f'Seçim:        {target_label}\n'
        f'Böyük:        {instance.adults_count}\n'
        f'Uşaq:         {instance.children_count}\n\n'
        'Qeyd:\n'
        f'{instance.note}\n\n'
        '────────────────────────────\n'
        f'Göndərilmə tarixi: {created_label}'
    )


def send_booking_notification(instance):
    try:
        services = [str(s) for s in instance.services.all()]
        packages = [str(p) for p in instance.packages.all()]
        target_name = ', '.join(services + packages) or 'Sifariş'
        subject = f'Yeni sifariş: {target_name} — {instance.full_name}'
        message = format_booking_message(instance)
        recipient = settings.EMAIL_HOST_USER
        if not recipient:
            logger.warning('Booking form email skipped: EMAIL_HOST_USER is not set.')
            return
        send_mail_func(recipient, subject, message)
    except Exception:
        logger.exception('Booking form notification email failed.')


def send_mail_func(user_email, custom_subject, custom_message):
    from_email = getattr(settings, 'EMAIL_HOST_USER', None) or settings.DEFAULT_FROM_EMAIL
    send_mail(
        custom_subject,
        custom_message,
        from_email,
        [user_email],
        fail_silently=False,
    )
