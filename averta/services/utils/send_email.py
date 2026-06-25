import html as html_lib
import logging
import re
from email.utils import formataddr

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
from django.utils.formats import date_format

logger = logging.getLogger(__name__)


def format_appeal_contact_message(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone = instance.phone.strip() if instance.phone else '—'
    email = (instance.email or '').strip()
    email_line = f'Email:        {email}\n' if email else ''

    return (
        f'Ad soyad:     {instance.full_name}\n'
        f'{email_line}'
        f'Mobil nömrə:  {phone}\n\n'
        'Mesaj:\n'
        f'{instance.info}\n\n'
        '────────────────────────────\n'
        f'Göndərilmə tarixi: {created_label}'
    )


def format_appeal_contact_message_html(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone_raw = instance.phone.strip() if instance.phone else ''
    wa_url = _whatsapp_url(phone_raw)
    if wa_url:
        phone_html = (
            f'<a href="{html_lib.escape(wa_url)}">'
            f'{html_lib.escape(phone_raw)}</a>'
        )
    else:
        phone_html = html_lib.escape(phone_raw or '—')

    email = (instance.email or '').strip()
    email_line = (
        f'Email:        <a href="mailto:{html_lib.escape(email)}">'
        f'{html_lib.escape(email)}</a><br>\n'
        if email else ''
    )

    return (
        f'Ad soyad:     {html_lib.escape(instance.full_name)}<br>\n'
        f'{email_line}'
        f'Mobil nömrə:  {phone_html}<br>\n'
        '<br>\n'
        'Mesaj:<br>\n'
        f'{html_lib.escape(instance.info)}<br>\n'
        '<br>\n'
        '────────────────────────────<br>\n'
        f'Göndərilmə tarixi: {html_lib.escape(created_label)}'
    )


def send_appeal_contact_notification(instance):
    try:
        subject = 'Saytdan gələn müraciət'
        message = format_appeal_contact_message(instance)
        html_message = format_appeal_contact_message_html(instance)
        recipient = settings.CONTACT_RECEIVER_EMAIL
        if not recipient:
            logger.warning('Contact form email skipped: CONTACT_RECEIVER_EMAIL is not set.')
            return
        send_mail_func(
            recipient=recipient,
            subject=subject,
            message=message,
            sender_name=instance.full_name,
            sender_email=(instance.email or '').strip(),
            html_message=html_message,
        )
    except Exception:
        logger.exception('Contact form notification email failed.')


def _whatsapp_url(phone):
    if not phone:
        return None
    digits = re.sub(r'\D', '', str(phone).strip())
    if not digits:
        return None
    if digits.startswith('994'):
        pass
    elif digits.startswith('0'):
        digits = '994' + digits[1:]
    elif len(digits) == 9:
        digits = '994' + digits
    return f'https://wa.me/{digits}'


def format_booking_message(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone = instance.phone.strip() if instance.phone else '—'
    email = (instance.email or '').strip()
    email_line = f'Email:            {email}\n' if email else ''
    note = instance.note.strip() if instance.note else '—'

    services = ', '.join(str(s) for s in instance.services.all()) or '—'
    packages = ', '.join(str(p) for p in instance.packages.all()) or '—'

    date_from = date_format(instance.date_from, 'd-m-Y') if instance.date_from else '—'
    date_to   = date_format(instance.date_to,   'd-m-Y') if instance.date_to   else '—'
    arrival_date = date_format(instance.arrival_date, 'd-m-Y') if instance.arrival_date else '—'

    return (
        f'Ad soyad:         {instance.full_name}\n'
        f'{email_line}'
        f'Mobil nömrə:      {phone}\n'
        f'Gediş tarixi:     {date_from}\n'
        f'Qayıdış tarixi:   {date_to}\n'
        f'Gəliş tarixi:     {arrival_date}\n'
        f'Böyüklər:         {instance.adults_count}\n'
        f'Uşaqlar:          {instance.children_count}\n'
        f'Xidmətlər:        {services}\n'
        f'Paketlər:         {packages}\n'
        f'Qeyd:             {note}\n\n'
        '────────────────────────────\n'
        f'Göndərilmə tarixi: {created_label}'
    )


def format_booking_message_html(instance):
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    phone_raw = instance.phone.strip() if instance.phone else ''
    wa_url = _whatsapp_url(phone_raw)
    if wa_url:
        phone_html = (
            f'<a href="{html_lib.escape(wa_url)}">'
            f'{html_lib.escape(phone_raw)}</a>'
        )
    else:
        phone_html = html_lib.escape(phone_raw or '—')

    email = (instance.email or '').strip()
    email_line = (
        f'Email:            <a href="mailto:{html_lib.escape(email)}">'
        f'{html_lib.escape(email)}</a><br>\n'
        if email else ''
    )
    note = html_lib.escape(instance.note.strip() if instance.note else '—')

    services = html_lib.escape(', '.join(str(s) for s in instance.services.all()) or '—')
    packages = html_lib.escape(', '.join(str(p) for p in instance.packages.all()) or '—')

    date_from = date_format(instance.date_from, 'd-m-Y') if instance.date_from else '—'
    date_to = date_format(instance.date_to, 'd-m-Y') if instance.date_to else '—'
    arrival_date = date_format(instance.arrival_date, 'd-m-Y') if instance.arrival_date else '—'

    return (
        f'Ad soyad:         {html_lib.escape(instance.full_name)}<br>\n'
        f'{email_line}'
        f'Mobil nömrə:      {phone_html}<br>\n'
        f'Gediş tarixi:     {html_lib.escape(date_from)}<br>\n'
        f'Qayıdış tarixi:   {html_lib.escape(date_to)}<br>\n'
        f'Gəliş tarixi:     {html_lib.escape(arrival_date)}<br>\n'
        f'Böyüklər:         {instance.adults_count}<br>\n'
        f'Uşaqlar:          {instance.children_count}<br>\n'
        f'Xidmətlər:        {services}<br>\n'
        f'Paketlər:         {packages}<br>\n'
        f'Qeyd:             {note}<br>\n'
        '<br>\n'
        '────────────────────────────<br>\n'
        f'Göndərilmə tarixi: {html_lib.escape(created_label)}'
    )


def _format_travel_dates(date_from, date_to, arrival_date=None):
    parts = [
        (date_from or '').strip(),
        (date_to or '').strip(),
        (arrival_date or '').strip(),
    ]
    parts = [p for p in parts if p]
    if not parts:
        return '—'
    return '\n'.join(parts)


def _excel_cell(value):
    text = '' if value is None else str(value)
    text = html_lib.escape(text).replace('\n', '<br/>')
    return text


def build_booking_xls(instance):
    """Admin paneldəki tək sifariş Excel exportu ilə eyni format."""
    created_at = instance.created_at
    if timezone.is_aware(created_at):
        created_at = timezone.localtime(created_at)
    created_label = date_format(created_at, 'd.m.Y H:i')

    date_from = date_format(instance.date_from, 'd-m-Y') if instance.date_from else ''
    date_to = date_format(instance.date_to, 'd-m-Y') if instance.date_to else ''
    arrival_date = date_format(instance.arrival_date, 'd-m-Y') if instance.arrival_date else ''

    services = ' | '.join(str(s) for s in instance.services.all())
    packages = ' | '.join(str(p) for p in instance.packages.all())

    headers = [
        'ID',
        'Tarix',
        'Ad soyad',
        'Mobil nömrə',
        'E-poçt',
        'Gediş / Qayıdış / Gəliş tarixi',
        'Qeyd',
        'Böyük sayı',
        'Uşaq sayı',
        'Xidmətlər',
        'Paketlər',
    ]
    row = [
        instance.pk,
        created_label,
        instance.full_name or '',
        instance.phone or '',
        instance.email or '',
        _format_travel_dates(date_from, date_to, arrival_date),
        instance.note or '',
        instance.adults_count,
        instance.children_count,
        services,
        packages,
    ]
    col_widths = [8, 22, 26, 18, 22, 16, 42, 10, 10, 38, 38]

    cols = ''.join(
        f'<col style="width:{w * 8}px" />'
        for w in col_widths
    )
    ths = ''.join(
        '<th style="border:1px solid #d1d5db; padding:7px; background:#13357b; '
        f'color:#fff; font-weight:700; text-align:left;">{html_lib.escape(h)}</th>'
        for h in headers
    )
    tds = ''.join(
        '<td style="border:1px solid #d1d5db; padding:6px; vertical-align:top; '
        f'white-space:pre-wrap;">{_excel_cell(v)}</td>'
        for v in row
    )

    content = (
        '<html xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:x="urn:schemas-microsoft-com:office:excel">'
        '<head><meta charset="utf-8" /></head><body>'
        '<table style="border-collapse:collapse; font-family:Arial, sans-serif; font-size:12px;">'
        f'<colgroup>{cols}</colgroup>'
        f'<thead><tr>{ths}</tr></thead>'
        f'<tbody><tr>{tds}</tr></tbody>'
        '</table>'
        '</body></html>'
    )

    now = timezone.localtime(timezone.now())
    filename = f'booking_{instance.pk}_{now:%Y-%m-%d_%H-%M}.xls'
    return filename, content.encode('utf-8')


def send_booking_notification(instance):
    try:
        subject = 'Saytdan gələn sifariş'
        message = format_booking_message(instance)
        html_message = format_booking_message_html(instance)
        recipient = settings.CONTACT_RECEIVER_EMAIL
        if not recipient:
            logger.warning('Booking email skipped: CONTACT_RECEIVER_EMAIL is not set.')
            return
        xls_filename, xls_content = build_booking_xls(instance)
        send_mail_func(
            recipient=recipient,
            subject=subject,
            message=message,
            sender_name=instance.full_name,
            sender_email=(instance.email or '').strip(),
            html_message=html_message,
            attachments=[(xls_filename, xls_content, 'application/vnd.ms-excel')],
        )
    except Exception:
        logger.exception('Booking notification email failed.')


def send_mail_func(
    recipient,
    subject,
    message,
    sender_name='',
    sender_email='',
    html_message=None,
    attachments=None,
):
    smtp_user = getattr(settings, 'EMAIL_HOST_USER', None) or settings.DEFAULT_FROM_EMAIL
    sender_name = (sender_name or '').strip()
    sender_email = (sender_email or '').strip()

    if sender_email:
        display = sender_email
        from_email = formataddr((display, smtp_user))
        reply_to = [formataddr((sender_name, sender_email)) if sender_name else sender_email]
    else:
        display = sender_name or smtp_user
        from_email = formataddr((display, smtp_user))
        reply_to = []

    if html_message:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to,
        )
        email.attach_alternative(html_message, 'text/html')
    else:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to,
        )
    for attachment in attachments or []:
        filename, content, mimetype = attachment
        email.attach(filename, content, mimetype)
    email.send(fail_silently=False)
