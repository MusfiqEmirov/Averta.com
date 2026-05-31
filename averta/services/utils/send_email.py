import logging
from email.utils import formataddr

from django.conf import settings
from django.core.mail import EmailMessage
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
        if not (instance.email or '').strip():
            logger.info('Contact form email skipped: sender email is empty.')
            return
        subject = f'Yeni əlaqə müraciəti: {instance.subject}'
        message = format_appeal_contact_message(instance)
        recipient = settings.CONTACT_RECEIVER_EMAIL
        if not recipient:
            logger.warning('Contact form email skipped: CONTACT_RECEIVER_EMAIL is not set.')
            return
        send_mail_func(
            recipient=recipient,
            subject=subject,
            message=message,
            sender_name=instance.full_name,
            sender_email=instance.email,
        )
    except Exception:
        logger.exception('Contact form notification email failed.')


def format_booking_message(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone = instance.phone.strip() if instance.phone else '—'
    email = instance.email.strip() if instance.email else '—'
    note = instance.note.strip() if instance.note else '—'

    services = ', '.join(str(s) for s in instance.services.all()) or '—'
    packages = ', '.join(str(p) for p in instance.packages.all()) or '—'

    date_from = date_format(instance.date_from, 'd-m-Y') if instance.date_from else '—'
    date_to   = date_format(instance.date_to,   'd-m-Y') if instance.date_to   else '—'

    return (
        'Yeni sifariş müraciəti\n'
        '────────────────────────────\n\n'
        f'Ad soyad:         {instance.full_name}\n'
        f'Email:            {email}\n'
        f'Mobil nömrə:      {phone}\n'
        f'Gediş tarixi:     {date_from}\n'
        f'Qayıdış tarixi:   {date_to}\n'
        f'Böyüklər:         {instance.adults_count}\n'
        f'Uşaqlar:          {instance.children_count}\n'
        f'Xidmətlər:        {services}\n'
        f'Paketlər:         {packages}\n'
        f'Qeyd:             {note}\n\n'
        '────────────────────────────\n'
        f'Göndərilmə tarixi: {created_label}'
    )


def send_booking_notification(instance):
    try:
        if not (instance.email or '').strip():
            logger.info('Booking email skipped: sender email is empty.')
            return
        subject = f'Yeni sifariş: {instance.full_name}'
        message = format_booking_message(instance)
        recipient = settings.CONTACT_RECEIVER_EMAIL
        if not recipient:
            logger.warning('Booking email skipped: CONTACT_RECEIVER_EMAIL is not set.')
            return
        send_mail_func(
            recipient=recipient,
            subject=subject,
            message=message,
            sender_name=instance.full_name,
            sender_email=instance.email or '',
        )
    except Exception:
        logger.exception('Booking notification email failed.')


def send_mail_func(recipient, subject, message, sender_name='', sender_email=''):
    smtp_user = getattr(settings, 'EMAIL_HOST_USER', None) or settings.DEFAULT_FROM_EMAIL

    if sender_email:
        display = sender_email
        from_email = formataddr((display, smtp_user))
        reply_to = [formataddr((sender_name, sender_email)) if sender_name else sender_email]
    else:
        from_email = smtp_user
        reply_to = []

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[recipient],
        reply_to=reply_to,
    )
    email.send(fail_silently=False)
