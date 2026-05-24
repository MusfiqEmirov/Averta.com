"""Admin paneli üçün aydın izahlar və menyu sırası."""

from django.contrib import admin

# Sol menyuda görünəcək sıra (Statistika birinci)
ADMIN_MODEL_ORDER = [
    'statistic',
    'motto',
    'about',
    'contact',
    'appealcontact',
    'service',
    'package',
    'partner',
    'blog',
    'faq',
    'media',
]


def patch_admin_site_order():
    original_get_app_list = admin.site.get_app_list

    def get_app_list(request, app_label=None):
        app_list = original_get_app_list(request, app_label)
        for app in app_list:
            if app.get('app_label') != 'services':
                continue
            order_map = {name: idx for idx, name in enumerate(ADMIN_MODEL_ORDER)}

            def sort_key(model_entry):
                name = model_entry.get('object_name', '').lower()
                return order_map.get(name, 999)

            app['models'].sort(key=sort_key)
        return app_list

    admin.site.get_app_list = get_app_list


class AdminPageHelpMixin:
    """Siyahı və redaktə səhifəsinin yuxarısında izah göstərir."""

    admin_page_help = ''
    change_list_template = 'admin/averta/change_list.html'
    change_form_template = 'admin/averta/change_form.html'

    class Media:
        css = {'all': ('assets/css/admin_help.css',)}

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = self.admin_page_help
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['admin_page_help'] = self.admin_page_help
        return super().changeform_view(request, object_id, form_url, extra_context)


# ---------------------------------------------------------------------------
# Səhifə izahları — saytda harada görünür
# ---------------------------------------------------------------------------

STATISTIC_HELP = (
    '<strong>Bu nədir?</strong> Ana səhifədə və Haqqımızda səhifəsində görünən 4 rəqəmli statistika bloku '
    '(məs: <em>25 — İllik təcrübə</em>).<br>'
    '<strong>Harada dəyişir?</strong> Sayt → Ana səhifə (aşağı hissə) və Haqqımızda səhifəsi.<br>'
    '<strong>Necə doldurulur?</strong> Hər kart üçün ikon seçin, böyük rəqəm yazın, altına qısa izahı 3 dildə əlavə edin. '
    'Adətən yalnız <strong>1 qeyd</strong> saxlanılır — mövcud olanı redaktə edin.'
)

MOTTO_HELP = (
    '<strong>Bu nədir?</strong> Saytın müxtəlif yerlərində görünən qısa deviz cümlələri.<br>'
    '<strong>Harada dəyişir?</strong><br>'
    '• <strong>Ana səhifə karuseli</strong> — yuxarıdakı böyük şəkil slayderində mətn.<br>'
    '• <strong>Daxili səhifələrin banneri</strong> — Haqqımızda, Əlaqə, Xidmətlər, Bloq səhifələrinin '
    'yuxarı fon şəklinin üstündə (deviz varsa). Deviz yoxdursa banner boş qalır.<br>'
    '<strong>Qeyd:</strong> Ana səhifə üçün bir neçə deviz əlavə edə bilərsiniz — '
    '«Ana səhifə karuselində göstər?» işarələnmiş hər deviz növbəti slaydda görünür. '
    'Daxili səhifə banneri üçün hər səhifədə bir deviz kifayətdir.'
)

ABOUT_HELP = (
    '<strong>Bu nədir?</strong> «Haqqımızda» səhifəsinin və ana səhifədəki qısa «Haqqımızda» blokunun məzmunu.<br>'
    '<strong>Harada dəyişir?</strong> Menyu → Haqqımızda; ana səhifədə «Haqqımızda» bölməsi.<br>'
    '<strong>Əlavə:</strong> «Səhifə şəkli» — yalnız bir şəkil. '
    'Video yuxarıdakı «Əsas tanıtım videosu» bölməsindədir.'
)

CONTACT_HELP = (
    '<strong>Bu nədir?</strong> Saytın ümumi əlaqə məlumatları — telefon, ünvan, e-poçt, sosial şəbəkələr.<br>'
    '<strong>Harada dəyişir?</strong> Menyu → Əlaqə səhifəsi, saytın alt hissəsi (footer), ana səhifə «Əlaqə» düyməsi.<br>'
    '<strong>Qeyd:</strong> Ziyarətçilərin göndərdiyi mesajlar burada deyil — onlar «Gələn mesajlar» bölməsindədir.'
)

APPEAL_HELP = (
    '<strong>Bu nədir?</strong> Ziyarətçilərin Əlaqə formasından göndərdiyi mesajlar.<br>'
    '<strong>Harada gəlir?</strong> Sayt → Əlaqə səhifəsi → «Mesaj göndər» forması.<br>'
    '<strong>Nə etməli?</strong> Mesajı oxuyun, «Oxunub» işarələyin. Yeni mesaj əlavə edə bilməzsiniz — '
    'yalnız saytdan gəlir.'
)

SERVICE_HELP = (
    '<strong>Bu nədir?</strong> Saytda təqdim olunan xidmətlər (tur, transfer, bələdçilik və s.).<br>'
    '<strong>Harada dəyişir?</strong> Menyu → Xidmətlər; ana səhifə xidmət blokları.<br>'
    '<strong>Şəkillər:</strong> Aşağıdakı «Xidmət şəkilləri» bölməsindən yükləyin. '
    '«Ana səhifədə göstərilsin?» — ən çox 6 xidmət.'
)

PACKAGE_HELP = (
    '<strong>Bu nədir?</strong> Tur paketləri — qiymət, bitiş tarixi və daxil olan xidmətlərlə.<br>'
    '<strong>Harada dəyişir?</strong> Menyu → Paketlər; ana səhifə paket kartları (aktiv, vaxtı keçməyən).<br>'
    '<strong>Xidmətlər:</strong> Paketə hansı xidmətlərin daxil olduğunu «Xidmətlər» sahəsindən seçin.<br>'
    '<strong>Şəkillər:</strong> «Paket şəkilləri» bölməsindən yükləyin.'
)

PARTNER_HELP = (
    '<strong>Bu nədir?</strong> Tərəfdaş şirkətlərin adı və loqosu.<br>'
    '<strong>Harada dəyişir?</strong> Ana səhifə və Haqqımızda səhifəsindəki tərəfdaşlar karuseli.<br>'
    '<strong>Qeyd:</strong> «Aktiv» söndürülərsə saytda görünməz. Loqonu aşağıdakı «Logo» bölməsindən yükləyin.'
)

BLOG_HELP = (
    '<strong>Bu nədir?</strong> Bloq yazıları — xəbər və məqalələr.<br>'
    '<strong>Harada dəyişir?</strong> Menyu → Bloq siyahısı; hər yazının ayrıca səhifəsi; ana səhifə '
    '(«Ana səhifədə olsun» — max 6 yazı).<br>'
    '<strong>Şəkil:</strong> Yazının üz qabığı — kartlarda və yazı səhifəsində görünür.'
)

FAQ_HELP = (
    '<strong>Bu nədir?</strong> Tez-tez verilən suallar və cavabları.<br>'
    '<strong>Harada dəyişir?</strong> Footer → FAQ səhifəsi (bütün aktiv suallar); '
    'ana səhifə FAQ bloku (yalnız «Ana səhifədə göstərilsin?» işarələnənlər, ən çox 6).<br>'
    '<strong>Sıra:</strong> Kiçik rəqəm = yuxarıda göstərilir. «Saytda göstərilsin?» söndürülərsə tam gizlənir.'
)

MEDIA_HELP = (
    '<strong>Bu nədir?</strong> Daxili səhifələrin yuxarı banner fon şəkilləri (Haqqımızda, Bloq və s.).<br>'
    '<strong>Harada dəyişir?</strong> Ana səhifə xaric bütün səhifələrin yuxarı geniş şəkil zolağı.<br>'
    '<strong>Qeyd:</strong> Xidmət, paket, tərəfdaş və qalereya şəkilləri burada deyil — həmin bölmələrin '
    'öz səhifəsindən yüklənir. Hər səhifə üçün yalnız <strong>bir</strong> fon şəkli işarələyin.'
)
