"""Admin sıra dropdown: 0 = ilk, 1 = sonrakı, …"""

from django import forms


def _position_label(position: int) -> str:
    if position == 0:
        return '0 — İlk'
    if position == 1:
        return '1 — Sonrakı'
    if position == 2:
        return '2 — 3-cü'
    if position == 3:
        return '3 — 4-cü'
    if position == 4:
        return '4 — 5-ci'
    return f'{position} — {position + 1}-ci'


def build_order_choices(queryset, instance=None, *, field_name='sort_order', extra_last=False):
    count = queryset.count()
    if instance is not None and instance.pk:
        current = getattr(instance, field_name, 0) or 0
        upper = max(count - 1, current)
    else:
        upper = count if extra_last else max(count - 1, 0)
    return [(i, _position_label(i)) for i in range(upper + 1)]


def apply_order_choice_field(form, *, model, instance=None, field_name='sort_order'):
    if field_name not in form.fields:
        return

    field = form.fields[field_name]
    is_new = instance is None or not instance.pk
    choices = build_order_choices(
        model.objects.all(),
        instance=instance,
        field_name=field_name,
        extra_last=is_new,
    )
    initial = 0
    if instance is not None and instance.pk:
        initial = getattr(instance, field_name, 0) or 0
    elif is_new:
        initial = model.objects.count()

    form.fields[field_name] = forms.TypedChoiceField(
        choices=choices,
        coerce=int,
        label=field.label,
        help_text=field.help_text or (
            '0 = ilk, 1 = sonrakı və s. '
            'Saxladıqda sayt, admin siyahısı və menyu dropdown-u yenilənir.'
        ),
        initial=initial,
        required=field.required,
    )
