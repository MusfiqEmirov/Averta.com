from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from services.utils.cache_utils import invalidate_model_cache
from services.admin.admin_help import (
    AdminPageHelpMixin,
    ABOUT_HELP,
    APPEAL_HELP,
    BOOKING_HELP,
    BLOG_HELP,
    CONTACT_HELP,
    FAQ_HELP,
    MEDIA_HELP,
    MOTTO_HELP,
    PARTNER_HELP,
    REVIEW_HELP,
    SERVICE_HELP,
    PACKAGE_HELP,
    STATISTIC_HELP,
    patch_admin_site_order,
)
from services.admin.order_fields import apply_order_choice_field

from services.admin.admin_filters import (
    CreatedAtMonthFilter,
    CreatedAtPeriodFilter,
    CreatedAtYearFilter,
    ReviewTargetFilter,
)
from services.forms.forms_v1 import BookingAdminForm
from services.models import (
    Media,
    Partner,
    About,
    Contact,
    AppealContact,
    Booking,
    Motto,
    Review,
    Statistic,
    Blog,
    FAQ,
    Service,
    Package,
)

admin.site.site_header = 'Averta — Sayt idarəetməsi'
admin.site.site_title = 'Averta Admin'
admin.site.index_title = 'Bölmə seçin — hər biri saytın müəyyən hissəsini idarə edir'
admin.site.empty_value_display = '—'

TIMESTAMP_READONLY = ('created_at', 'updated_at')


class AdminImageCompressMixin:
    """Browser-side image compression for admin forms that upload images."""

    class Media:
        js = ('assets/js/admin_image_compress.js',)


# ---------------------------------------------------------------------------
# Admin forms (CKEditor for rich-text description fields)
# ---------------------------------------------------------------------------

class AboutAdminForm(forms.ModelForm):
    class Meta:
        model = About
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }


class MediaAdminForm(forms.ModelForm):
    """Background images only; content images belong on related model inlines."""

    class Meta:
        model = Media
        fields = (
            'image',
            'is_home_page_background_image',
            'is_about_page_background_image',
            'is_contact_page_background_image',
            'is_service_page_background_image',
            'is_blog_page_background_image',
            'is_home_contact_background_image',
            'is_contact_booking_background_image',
        )


# ---------------------------------------------------------------------------
# Content inlines (no background-image flags)
# ---------------------------------------------------------------------------

class ContentMediaInline(admin.TabularInline):
    model = Media
    extra = 1
    fields = ('image_preview', 'image', 'video')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.image.url)
        return '—'

    image_preview.short_description = _('Önizləmə')


class PartnerMediaInline(ContentMediaInline):
    fk_name = 'partner'
    verbose_name = 'Logo'
    verbose_name_plural = 'Logo'
    max_num = 1
    extra = 1
    fields = ('image_preview', 'image')
    readonly_fields = ('image_preview',)


class ServiceMediaInline(ContentMediaInline):
    fk_name = 'service'
    verbose_name = 'Şəkil'
    verbose_name_plural = 'Xidmət şəkilləri'
    extra = 1


class PackageMediaInline(ContentMediaInline):
    fk_name = 'package'
    verbose_name = 'Şəkil'
    verbose_name_plural = 'Paket şəkli'
    max_num = 1
    extra = 1
    fields = ('image_preview', 'image')
    readonly_fields = ('image_preview',)


class AboutMediaInline(admin.TabularInline):
    """Haqqımızda — qaleriya şəkilləri (çoxlu)."""

    model = Media
    fk_name = 'about'
    max_num = 20
    min_num = 0
    extra = 1
    verbose_name = 'Qaleriya şəkli'
    verbose_name_plural = 'Qaleriya şəkilləri'
    classes = ('wide',)
    fields = ('image_preview', 'image')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'

    image_preview.short_description = _('Önizləmə')


# ---------------------------------------------------------------------------
# Service & Package
# ---------------------------------------------------------------------------

class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_order_choice_field(
            self,
            model=Service,
            instance=self.instance,
            field_name='sort_order',
        )


@admin.register(Service)
class ServiceAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    form = ServiceAdminForm
    admin_page_help = SERVICE_HELP
    save_on_top = True
    list_display = (
        'name_az',
        'is_active',
        'on_main_page',
        'created_at',
        'updated_at',
        'sort_order',
    )
    list_filter = ('is_active', 'on_main_page')
    search_fields = ('name_az', 'name_en', 'name_ru', 'slug')
    list_editable = ('sort_order', 'is_active', 'on_main_page')
    ordering = ('sort_order', 'id')
    readonly_fields = ('slug',) + TIMESTAMP_READONLY
    inlines = [ServiceMediaInline]
    fieldsets = (
        (_('Sıra'), {
            'fields': ('sort_order',),
            'description': _(
                '0 = ilk (sayt, admin siyahısı, menyu dropdown). '
                '1 = sonrakı və s. Eyni sıra təkrarlanarsa saxlayanda avtomatik düzəlir.'
            ),
        }),
        (_('Azərbaycan'), {
            'fields': ('name_az', 'description_az', 'bullet_list_az'),
            'classes': ('wide',),
        }),
        (_('English'), {
            'fields': ('name_en', 'description_en', 'bullet_list_en'),
            'classes': ('wide', 'g-lang-en'),
        }),
        (_('Русский'), {
            'fields': ('name_ru', 'description_ru', 'bullet_list_ru'),
            'classes': ('wide', 'g-lang-ru'),
        }),
        (_('Parametrlər'), {
            'fields': ('is_active', 'on_main_page', 'slug') + TIMESTAMP_READONLY,
            'description': _(
                '«Saytda göstərilsin?» söndürülərsə xidmət saytda gizlənir. '
                '«Ana səhifədə göstərilsin?» — ən çox 6 xidmət.'
            ),
        }),
    )


class PackageAdminForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = '__all__'
        widgets = {
            'description_az': CKEditorWidget(),
            'description_en': CKEditorWidget(),
            'description_ru': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_order_choice_field(
            self,
            model=Package,
            instance=self.instance,
            field_name='sort_order',
        )

    def clean(self):
        cleaned_data = super().clean()
        selected = sum(
            1 for name in ('show_date_from', 'show_date_to', 'show_arrival_date')
            if cleaned_data.get(name)
        )
        if selected > 2:
            raise ValidationError(
                _('Sifariş formunda eyni anda ən çoxu 2 tarix sahəsi seçilə bilər.')
            )
        return cleaned_data


@admin.register(Package)
class PackageAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = PACKAGE_HELP
    form = PackageAdminForm
    filter_horizontal = ('service',)
    list_display = ('name_az', 'sort_order', 'price', 'currency', 'price_from', 'end_date', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name_az', 'name_en', 'name_ru', 'slug')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order', 'id')
    readonly_fields = ('slug',) + TIMESTAMP_READONLY
    fieldsets = (
        (_('Sıra'), {
            'fields': ('sort_order',),
            'description': _(
                '0 = ilk (ana səhifə paket karuseli, sifariş forması). '
                '1 = sonrakı və s. Eyni sıra təkrarlanarsa saxladıqda avtomatik düzəlir.'
            ),
        }),
        (_('Xidmətlər'), {
            'fields': ('service',),
            'description': _(
                'Paketə daxil olan xidmətləri seçin. Bir paketə bir neçə xidmət əlavə edə bilərsiniz.'
            ),
        }),
        (_('Azərbaycan'), {
            'fields': ('name_az', 'description_az'),
            'classes': ('wide',),
        }),
        (_('English'), {
            'fields': ('name_en', 'description_en'),
            'classes': ('wide', 'g-lang-en'),
        }),
        (_('Русский'), {
            'fields': ('name_ru', 'description_ru'),
            'classes': ('wide', 'g-lang-ru'),
        }),
        (_('Şəkil'), {
            'fields': ('image',),
            'description': _('Paket kartının yuxarı hissəsində göstərilir.'),
        }),
        (_('Qiymət və tarix'), {
            'fields': ('price', 'currency', 'price_from', 'end_date'),
            'description': _(
                '«dan/dən» işarələnərsə AZ dilində «$909-dan» formatında göstərilir. '
                'Bitiş tarixi keçəndən sonra paket saytda avtomatik gizlənir.'
            ),
        }),
        (_('Sifariş formu'), {
            'fields': ('show_date_from', 'show_date_to', 'show_arrival_date'),
            'description': _(
                'Sifariş formunda hansı tarix sahələrinin göstəriləcəyini seçin. '
                'Eyni anda ən çoxu 2 sahə seçilə bilər.'
            ),
        }),
        (_('Parametrlər'), {
            'fields': ('is_active', 'slug') + TIMESTAMP_READONLY,
            'description': _(
                'Paketin saytda görünməsi üçün «Saytda göstərilsin?» işarəli olmalıdır. '
                'Söndürülərsə paket saytda və sifariş formasında gizlənir.'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_active is None:
            obj.is_active = True
        super().save_model(request, obj, form, change)
        invalidate_model_cache('Package')


# ---------------------------------------------------------------------------
# Partner
# ---------------------------------------------------------------------------

@admin.register(Partner)
class PartnerAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = PARTNER_HELP
    list_display = ('name_az', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name_az', 'name_en', 'name_ru')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    readonly_fields = TIMESTAMP_READONLY
    inlines = [PartnerMediaInline]
    fieldsets = (
        (_('Azərbaycan'), {'fields': ('name_az',)}),
        (_('English'), {'fields': ('name_en',), 'classes': ('wide', 'g-lang-en')}),
        (_('Русский'), {'fields': ('name_ru',), 'classes': ('wide', 'g-lang-ru')}),
        # (_('Sosial şəbəkələr'), {'fields': ('instagram', 'facebook', 'linkedn')}),
        (_('Parametrlər'), {
            'fields': ('is_active',),
            'description': _('«Saytda göstərilsin?» söndürülərsə loqo karuseldə görünməz.'),
        }),
        (_('Sistem məlumatı'), {'fields': TIMESTAMP_READONLY}),
    )


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

@admin.register(About)
class AboutAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = ABOUT_HELP
    form = AboutAdminForm
    list_display = ('main_title_az',)
    search_fields = ('main_title_az',)
    inlines = [AboutMediaInline]
    fieldsets = (
        (_('Azərbaycan'), {'fields': ('main_title_az', 'second_title_az', 'description_az'), 'classes': ('wide',)}),
        (_('English'), {'fields': ('main_title_en', 'second_title_en', 'description_en'), 'classes': ('wide', 'g-lang-en')}),
        (_('Русский'), {'fields': ('main_title_ru', 'second_title_ru', 'description_ru'), 'classes': ('wide', 'g-lang-ru')}),
        (_('Əsas tanıtım videosu (yalnız 1)'), {
            'fields': ('video', 'video_poster'),
            'description': _(
                'Haqqımızda səhifəsində play düyməsi ilə açılan video. '
                'Aşağıda qaleriya üçün çoxlu şəkil əlavə edə bilərsiniz — 3-dən çox olduqda karusel kimi göstərilir.'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_model_cache('about')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, Media) and instance.about_id:
                instance.video = None
            instance.save()
        formset.save_m2m()
        invalidate_model_cache('about')


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

@admin.register(Contact)
class ContactAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = CONTACT_HELP
    list_display = ('address_az', 'phone', 'email', 'instagram', 'facebook')
    search_fields = ('address_az', 'phone', 'email')
    fieldsets = (
        (_('Ünvan (saytda və footer-də)'), {'fields': ('address_az', 'address_en', 'address_ru')}),
        (_('Xəritə'), {
            'fields': ('map_embed_url',),
            'description': _('Əlaqə səhifəsində Google Xəritə bloku.'),
        }),
        (_('Telefon və WhatsApp'), {'fields': ('phone', 'whatsapp_number')}),
        (_('E-poçt və sosial şəbəkələr'), {
            'fields': ('email', 'email_two', 'instagram', 'facebook', 'youtube', 'linkedn', 'tiktok'),
            'description': _('Footer və Əlaqə səhifəsində ikon/link kimi görünür.'),
        }),
    )


# ---------------------------------------------------------------------------
# AppealContact
# ---------------------------------------------------------------------------

def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True, updated_at=timezone.now())


mark_as_read.short_description = _('Seçilmişləri oxunmuş kimi işarələ')


def mark_as_unread(modeladmin, request, queryset):
    queryset.update(is_read=False, updated_at=timezone.now())


mark_as_unread.short_description = _('Seçilmişləri oxunmamış kimi işarələ')


@admin.register(AppealContact)
class AppealContactAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = APPEAL_HELP
    list_display = ('full_name', 'email', 'phone', 'subject', 'is_read', 'created_at', 'updated_at')
    list_filter = (
        CreatedAtPeriodFilter,
        CreatedAtYearFilter,
        CreatedAtMonthFilter,
        'is_read',
    )
    search_fields = ('full_name', 'email', 'phone', 'subject')
    ordering = ('-created_at',)
    readonly_fields = ('full_name', 'email', 'phone', 'subject', 'info') + TIMESTAMP_READONLY
    actions = [mark_as_read, mark_as_unread]

    def has_add_permission(self, request):
        return False


@admin.register(Booking)
class BookingAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = BOOKING_HELP
    form = BookingAdminForm
    change_form_template = 'admin/averta/booking_change_form.html'
    change_list_template = 'admin/averta/booking_change_list_exports.html'
    list_display = (
        'full_name',
        'booking_target',
        'date_from_display',
        'date_to_display',
        'arrival_date_display',
        'adults_count',
        'children_count',
        'email',
        'phone',
        'is_read',
        'is_customer',
        'is_deleted',
        'created_at',
        'updated_at',
    )
    list_filter = (
        CreatedAtPeriodFilter,
        CreatedAtYearFilter,
        CreatedAtMonthFilter,
        'is_read',
        'is_customer',
        'is_deleted',
        'services',
        'packages',
    )
    search_fields = ('full_name', 'email', 'phone', 'note')
    ordering = ('-created_at',)
    list_editable = ('is_read', 'is_customer', 'is_deleted')
    readonly_fields = (
        'full_name',
        'email',
        'phone',
        'date_from_display',
        'date_to_display',
        'arrival_date_display',
        'note',
        'services',
        'packages',
        'adults_count',
        'children_count',
    ) + TIMESTAMP_READONLY
    actions = [mark_as_read, mark_as_unread]
    fieldsets = (
        (_('Müştəri'), {
            'fields': ('full_name', 'email', 'phone', 'note'),
        }),
        (_('Sifariş'), {
            'fields': ('services', 'packages', 'date_from_display', 'date_to_display', 'arrival_date_display', 'adults_count', 'children_count'),
        }),
        (_('Status'), {
            'fields': ('is_read', 'is_customer', 'is_deleted') + TIMESTAMP_READONLY,
        }),
    )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('services', 'packages')

    def booking_export_payload(self, obj):
        services = [str(s) for s in obj.services.all()]
        packages = [str(p) for p in obj.packages.all()]
        target_labels = services + packages
        return {
            'id': obj.pk,
            'created_at': date_format(timezone.localtime(obj.created_at), 'd.m.Y H:i') if obj.created_at else '',
            'full_name': obj.full_name or '',
            'phone': obj.phone or '',
            'email': obj.email or '',
            'date_from': date_format(obj.date_from, 'd-m-Y') if obj.date_from else '',
            'date_to': date_format(obj.date_to, 'd-m-Y') if obj.date_to else '',
            'arrival_date': date_format(obj.arrival_date, 'd-m-Y') if obj.arrival_date else '',
            'note': obj.note or '',
            'adults_count': obj.adults_count,
            'children_count': obj.children_count,
            'booking_target': ', '.join(target_labels) if target_labels else '—',
            'services': services,
            'packages': packages,
            'is_read': bool(obj.is_read),
            'is_customer': bool(obj.is_customer),
            'is_deleted': bool(obj.is_deleted),
        }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        response = super().changelist_view(request, extra_context=extra_context)
        if isinstance(response, TemplateResponse):
            cl = response.context_data.get('cl')
            if cl is not None:
                response.context_data['booking_export_json'] = [
                    self.booking_export_payload(obj) for obj in cl.result_list
                ]
        return response

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            obj = self.get_object(request, object_id)
            if obj is not None:
                extra_context['booking_export_json'] = self.booking_export_payload(obj)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        return True

    class Media(AdminPageHelpMixin.Media):
        css = {
            'all': (
                'assets/css/admin_help.css',
                'assets/css/admin_booking.css',
            ),
        }
        js = (
            'assets/js/admin_booking_export.js',
        )

    @admin.display(description=_('Gediş tarixi'), ordering='date_from')
    def date_from_display(self, obj):
        if not obj.date_from:
            return '—'
        return date_format(obj.date_from, 'd-m-Y')

    @admin.display(description=_('Qayıdış tarixi'), ordering='date_to')
    def date_to_display(self, obj):
        if not obj.date_to:
            return '—'
        return date_format(obj.date_to, 'd-m-Y')

    @admin.display(description=_('Gəliş tarixi'), ordering='arrival_date')
    def arrival_date_display(self, obj):
        if not obj.arrival_date:
            return '—'
        return date_format(obj.arrival_date, 'd-m-Y')

    @admin.display(description=_('Seçim'))
    def booking_target(self, obj):
        labels = [str(s) for s in obj.services.all()]
        labels += [str(p) for p in obj.packages.all()]
        if not labels:
            return '—'
        return format_html(
            '<span class="review-admin-target">{}</span>',
            ', '.join(labels),
        )


# ---------------------------------------------------------------------------
# Motto
# ---------------------------------------------------------------------------

@admin.register(Motto)
class MottoAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = MOTTO_HELP
    list_display = (
        '__str__',
        'show_on_home_hero',
        'is_about_page',
        'is_contact_page',
        'is_service_page',
        'is_package_page',
        'is_blog_page',
    )
    list_filter = (
        'show_on_home_hero',
        'is_about_page',
        'is_contact_page',
        'is_service_page',
        'is_package_page',
        'is_blog_page',
    )
    fieldsets = (
        (_('Azərbaycan'), {'fields': ('text_az',)}),
        (_('English'), {'fields': ('text_en',), 'classes': ('wide', 'g-lang-en')}),
        (_('Русский'), {'fields': ('text_ru',), 'classes': ('wide', 'g-lang-ru')}),
        (_('Harada göstərilsin?'), {
            'fields': (
                'show_on_home_hero',
                'is_about_page',
                'is_contact_page',
                'is_service_page',
                'is_package_page',
                'is_blog_page',
            ),
            'description': _(
                'Ana səhifə karuseli — yuxarı slayder. '
                'Digər seçimlər — həmin səhifənin yuxarı banner fon şəklinin üstündə deviz mətni. '
                'Deviz yoxdursa banner boş qalır, amma fon şəkli görünür.'
            ),
        }),
    )


# ---------------------------------------------------------------------------
# Statistic
# ---------------------------------------------------------------------------

@admin.register(Statistic)
class StatisticAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = STATISTIC_HELP
    fieldsets = (
        (_('1-ci statistika kartı (soldan birinci)'), {
            'fields': (
                'icon_one',
                'value_one',
                'caption_one_az',
                'caption_one_en',
                'caption_one_ru',
            ),
            'description': _('İkon, böyük rəqəm və alt yazı. Məs: 25 — İllik təcrübə'),
        }),
        (_('2-ci statistika kartı'), {
            'fields': (
                'icon_two',
                'value_two',
                'caption_two_az',
                'caption_two_en',
                'caption_two_ru',
            ),
        }),
        (_('3-cü statistika kartı'), {
            'fields': (
                'icon_three',
                'value_three',
                'caption_three_az',
                'caption_three_en',
                'caption_three_ru',
            ),
        }),
        (_('4-cü statistika kartı (sağdan sonuncu)'), {
            'fields': (
                'icon_four',
                'value_four',
                'caption_four_az',
                'caption_four_en',
                'caption_four_ru',
            ),
        }),
    )
    list_display = (
        '__str__',
        'value_one',
        'caption_one_az',
        'value_two',
        'caption_two_az',
        'value_three',
        'caption_three_az',
        'value_four',
        'caption_four_az',
    )


# ---------------------------------------------------------------------------
# Media (page background images only)
# ---------------------------------------------------------------------------

@admin.register(Media)
class MediaAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = MEDIA_HELP
    """Yalnız səhifə fon şəkilləri: xidmət/partnyor/Haqqımızda inlaynlərində yaradılan media burada görünmür."""

    form = MediaAdminForm
    list_display = (
        'image_preview',
        'is_home_page_background_image',
        'is_about_page_background_image',
        'is_contact_page_background_image',
        'is_service_page_background_image',
        'is_blog_page_background_image',
        'is_home_contact_background_image',
        'is_contact_booking_background_image',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'is_home_page_background_image',
        'is_about_page_background_image',
        'is_contact_page_background_image',
        'is_service_page_background_image',
        'is_blog_page_background_image',
        'is_home_contact_background_image',
        'is_contact_booking_background_image',
    )
    ordering = ('-created_at',)
    readonly_fields = ('image_preview',) + TIMESTAMP_READONLY

    fieldsets = (
        (_('Şəkil'), {'fields': ('image_preview', 'image')}),
        (_('Hansı səhifənin yuxarı banner fonudur?'), {
            'fields': (
                'is_home_page_background_image',
                'is_about_page_background_image',
                'is_contact_page_background_image',
                'is_service_page_background_image',
                'is_blog_page_background_image',
                'is_home_contact_background_image',
                'is_contact_booking_background_image',
            ),
            'description': _(
                'Yalniz bir sehife secin. '
                '"Ana sehife Elaqe bolmesi" — ana sehifede asagidaki "Elaqe/Bize yazin" '
                'formasinin arxa fonu. '
                '"Elaqe sehifesi Sifaris et bolmesi" — elaqe sehifesindeki booking '
                'formasinin arxa fonu.'
            ),
        }),
        (_('Sistem məlumatı'), {'fields': TIMESTAMP_READONLY}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.image.url)
        return '—'

    image_preview.short_description = _('Önizləmə')

    def get_queryset(self, request):
        """Inlayndan gələn kontent mediaya qarışmasın."""
        qs = super().get_queryset(request)
        return qs.filter(
            about__isnull=True,
            partner__isnull=True,
            service__isnull=True,
            package__isnull=True,
        )

    def save_model(self, request, obj, form, change):
        obj.about = None
        obj.partner = None
        obj.service = None
        obj.package = None
        obj.video = None
        super().save_model(request, obj, form, change)


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

@admin.register(FAQ)
class FAQAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = FAQ_HELP
    list_display = ('question_az', 'sort_order', 'is_active', 'on_main_page', 'created_at', 'updated_at')
    list_editable = ('sort_order', 'is_active', 'on_main_page')
    list_filter = ('is_active', 'on_main_page')
    search_fields = ('question_az', 'question_en', 'question_ru', 'answer_az')
    ordering = ('sort_order', 'id')
    readonly_fields = TIMESTAMP_READONLY
    fieldsets = (
        (_('Azərbaycan'), {'fields': ('question_az', 'answer_az'), 'classes': ('wide',)}),
        (_('English'), {'fields': ('question_en', 'answer_en'), 'classes': ('wide', 'g-lang-en')}),
        (_('Русский'), {'fields': ('question_ru', 'answer_ru'), 'classes': ('wide', 'g-lang-ru')}),
        (_('Parametrlər'), {
            'fields': ('sort_order', 'is_active', 'on_main_page'),
            'description': _(
                'Sıra nömrəsi kiçik olanda sual yuxarıda görünür. '
                '«Saytda göstərilsin?» söndürülərsə tam gizlənir. '
                '«Ana səhifədə göstərilsin?» yalnız ana səhifə FAQ blokuna təsir edir (ən çox 6).'
            ),
        }),
        (_('Sistem məlumatı'), {'fields': TIMESTAMP_READONLY}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_model_cache('FAQ')


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

@admin.register(Blog)
class BlogAdmin(AdminImageCompressMixin, AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = BLOG_HELP
    form = BlogAdminForm
    list_display = ('image_preview', 'topic_az', 'name_az', 'slug', 'date', 'on_main_page', 'view_count', 'created_at', 'updated_at')
    search_fields = ('name_az', 'name_en', 'name_ru', 'topic_az', 'topic_en', 'topic_ru', 'slug')
    list_filter = ('on_main_page',)
    ordering = ('-date', '-created_at')
    readonly_fields = ('image_preview', 'slug', 'view_count') + TIMESTAMP_READONLY
    fieldsets = (
        (_('Azərbaycan'), {'fields': ('topic_az', 'name_az', 'description_az'), 'classes': ('wide',)}),
        (_('English'), {'fields': ('topic_en', 'name_en', 'description_en'), 'classes': ('wide', 'g-lang-en')}),
        (_('Русский'), {'fields': ('topic_ru', 'name_ru', 'description_ru'), 'classes': ('wide', 'g-lang-ru')}),
        (_('Media'), {'fields': ('image_preview', 'image')}),
        (_('Parametrlər'), {
            'fields': ('date', 'on_main_page', 'slug', 'view_count') + TIMESTAMP_READONLY,
            'description': _(
                'Tarix — yazının dərc tarixi. '
                '«Ana səhifədə göstərilsin?» — ana səhifə bloq bölməsində (max 6). '
                'Slug avtomatik yaradılır (başlıqdan); URL: /blog/slug/. '
                'Baxış sayı avtomatik sayılır.'
            ),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.image.url)
        return '—'

    image_preview.short_description = _('Önizləmə')


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

def mark_review_active(modeladmin, request, queryset):
    queryset.update(is_active=True, updated_at=timezone.now())


mark_review_active.short_description = _('Seçilmişləri aktiv et (saytda göstər)')


def mark_review_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False, updated_at=timezone.now())


mark_review_inactive.short_description = _('Seçilmişləri deaktiv et (saytdan gizlət)')


def mark_review_read(modeladmin, request, queryset):
    queryset.update(is_read=True, updated_at=timezone.now())


mark_review_read.short_description = _('Seçilmişləri oxunmuş kimi işarələ')


def mark_review_unread(modeladmin, request, queryset):
    queryset.update(is_read=False, updated_at=timezone.now())


mark_review_unread.short_description = _('Seçilmişləri oxunmamış kimi işarələ')


@admin.register(Review)
class ReviewAdmin(AdminPageHelpMixin, admin.ModelAdmin):
    admin_page_help = REVIEW_HELP
    change_list_template = 'admin/averta/review_change_list.html'
    change_form_template = 'admin/averta/review_change_form.html'
    list_display = (
        'name',
        'rating_stars',
        'review_target_display',
        'short_message_display',
        'created_at_display',
        'status_badges',
        'is_read',
        'is_active',
    )
    list_display_links = ('name',)
    list_filter = (
        CreatedAtPeriodFilter,
        CreatedAtYearFilter,
        CreatedAtMonthFilter,
        ReviewTargetFilter,
        'is_read',
        'is_active',
        'rating',
        'service',
        'package',
    )
    search_fields = (
        'name', 'message',
        'service__name_az', 'package__name_az',
    )
    list_editable = ('is_read', 'is_active')
    ordering = ('-created_at',)
    readonly_fields = TIMESTAMP_READONLY
    actions = [mark_review_active, mark_review_inactive, mark_review_read, mark_review_unread]

    class Media(AdminPageHelpMixin.Media):
        css = {
            'all': (
                'assets/css/admin_help.css',
                'assets/css/admin_review.css',
            ),
        }

    fieldsets = (
        (_('Müştəri'), {
            'fields': ('name',),
        }),
        (_('Rəy məzmunu'), {
            'fields': ('message', 'rating', 'service', 'package'),
            'classes': ('wide',),
            'description': _('Yalnız xidmət və ya paket seçin, hər ikisi yox.'),
        }),
        (_('Moderasiya'), {
            'fields': ('is_read', 'is_active') + TIMESTAMP_READONLY,
            'description': _(
                '«Oxunub» — rəyi nəzərdən keçirdiyinizi qeyd edin. '
                '«Aktiv» — saytda göstərilir. Yeni rəylər deaktiv gəlir.'
            ),
        }),
    )

    @admin.display(description=_('Reytinq'))
    def rating_stars(self, obj):
        filled = '★' * obj.rating
        empty = '☆' * (5 - obj.rating)
        return format_html(
            '<span class="review-admin-stars" title="{} / 5">'
            '{}<span class="review-admin-stars-empty">{}</span></span>',
            obj.rating, filled, empty,
        )

    @admin.display(description=_('Xidmət / Paket'))
    def review_target_display(self, obj):
        label = '—'
        if obj.service_id:
            label = obj.service.name_az
        elif obj.package_id:
            label = obj.package.name_az
        if label == '—':
            return label
        return format_html(
            '<span class="review-admin-target" title="{}">{}</span>',
            label, label,
        )

    @admin.display(description=_('Rəy'))
    def short_message_display(self, obj):
        text = obj.message[:100] + '…' if len(obj.message) > 100 else obj.message
        return format_html(
            '<span class="review-admin-message" title="{}">{}</span>',
            obj.message, text,
        )

    @admin.display(description=_('Tarix'), ordering='created_at')
    def created_at_display(self, obj):
        return format_html(
            '<span class="review-admin-date">{}</span>',
            obj.created_at.strftime('%d.%m.%Y %H:%M'),
        )

    @admin.display(description=_('Status'))
    def status_badges(self, obj):
        badges = []
        if not obj.is_read:
            badges.append('<span class="review-badge review-badge--unread">Yeni</span>')
        else:
            badges.append('<span class="review-badge review-badge--read">Oxunub</span>')
        if obj.is_active:
            badges.append('<span class="review-badge review-badge--active">Saytda</span>')
        else:
            badges.append('<span class="review-badge review-badge--hidden">Gizli</span>')
        return format_html(
            '<div class="review-admin-badges">{}</div>',
            mark_safe(''.join(badges)),
        )


patch_admin_site_order()
