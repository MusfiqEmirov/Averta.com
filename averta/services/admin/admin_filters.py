from datetime import datetime, timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

_AZ_MONTHS = {
    1: 'Yanvar',
    2: 'Fevral',
    3: 'Mart',
    4: 'Aprel',
    5: 'May',
    6: 'İyun',
    7: 'İyul',
    8: 'Avqust',
    9: 'Sentyabr',
    10: 'Oktyabr',
    11: 'Noyabr',
    12: 'Dekabr',
}


def _start_of_day(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_month(dt):
    return _start_of_day(dt.replace(day=1))


def _start_of_year(dt):
    return _start_of_day(dt.replace(month=1, day=1))


class CreatedAtPeriodFilter(admin.SimpleListFilter):
    """Göndərilmə tarixinə görə sürətli dövr filtrləri."""

    title = _('Göndərilmə vaxtı')
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Bugün')),
            ('yesterday', _('Dünən')),
            ('last_7', _('Son 7 gün')),
            ('last_30', _('Son 30 gün')),
            ('last_90', _('Son 3 ay')),
            ('this_month', _('Bu ay')),
            ('last_month', _('Keçən ay')),
            ('this_year', _('Bu il')),
            ('last_year', _('Keçən il')),
            ('older', _('1 ildən köhnə')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        now = timezone.now()
        today = _start_of_day(now)

        if value == 'today':
            return queryset.filter(created_at__gte=today)

        if value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(created_at__gte=yesterday, created_at__lt=today)

        if value == 'last_7':
            return queryset.filter(created_at__gte=today - timedelta(days=7))

        if value == 'last_30':
            return queryset.filter(created_at__gte=today - timedelta(days=30))

        if value == 'last_90':
            return queryset.filter(created_at__gte=today - timedelta(days=90))

        if value == 'this_month':
            return queryset.filter(created_at__gte=_start_of_month(now))

        if value == 'last_month':
            this_month_start = _start_of_month(now)
            prev_month_end = this_month_start
            prev_month_start = _start_of_month(this_month_start - timedelta(days=1))
            return queryset.filter(
                created_at__gte=prev_month_start,
                created_at__lt=prev_month_end,
            )

        if value == 'this_year':
            return queryset.filter(created_at__gte=_start_of_year(now))

        if value == 'last_year':
            this_year_start = _start_of_year(now)
            last_year_start = this_year_start.replace(year=this_year_start.year - 1)
            return queryset.filter(
                created_at__gte=last_year_start,
                created_at__lt=this_year_start,
            )

        if value == 'older':
            this_year_start = _start_of_year(now)
            last_year_start = this_year_start.replace(year=this_year_start.year - 1)
            return queryset.filter(created_at__lt=last_year_start)

        return queryset


class CreatedAtYearFilter(admin.SimpleListFilter):
    """Mesajların göndərildiyi illər üzrə filtr."""

    title = _('İl')
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = (
            model_admin.model.objects
            .dates('created_at', 'year', order='DESC')
        )
        return [(str(d.year), str(d.year)) for d in years]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(created_at__year=int(value))


class CreatedAtMonthFilter(admin.SimpleListFilter):
    """Seçilmiş ilə uyğun aylar üzrə filtr (il seçilməyibsə — cari il)."""

    title = _('Ay')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        year_param = request.GET.get('year')
        qs = model_admin.model.objects.all()
        if year_param and year_param.isdigit():
            year = int(year_param)
            qs = qs.filter(created_at__year=year)
            months = qs.dates('created_at', 'month', order='DESC')
            return [
                (str(d.month), _AZ_MONTHS.get(d.month, str(d.month)))
                for d in months
            ]

        year = timezone.now().year
        qs = qs.filter(created_at__year=year)
        months = qs.dates('created_at', 'month', order='DESC')
        if months:
            return [
                (str(d.month), f'{_AZ_MONTHS.get(d.month, d.month)} {d.year}')
                for d in months
            ]

        return [
            (str(m), name)
            for m, name in sorted(_AZ_MONTHS.items(), reverse=True)
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        month = int(value)
        year_param = request.GET.get('year')
        if year_param and year_param.isdigit():
            year = int(year_param)
        else:
            year = timezone.now().year

        start = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_exclusive = timezone.make_aware(datetime(year + 1, 1, 1))
        else:
            end_exclusive = timezone.make_aware(datetime(year, month + 1, 1))
        return queryset.filter(created_at__gte=start, created_at__lt=end_exclusive)


class ReviewTargetFilter(admin.SimpleListFilter):
    """Rəyin xidmət, paket və ya ümumi olmasına görə filtr."""

    title = _('Rəy növü')
    parameter_name = 'review_target'

    def lookups(self, request, model_admin):
        return (
            ('service', _('Xidmət')),
            ('package', _('Paket')),
            ('general', _('Ümumi (xidmət/paket yox)')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'service':
            return queryset.filter(service__isnull=False)
        if value == 'package':
            return queryset.filter(package__isnull=False)
        if value == 'general':
            return queryset.filter(service__isnull=True, package__isnull=True)
        return queryset
