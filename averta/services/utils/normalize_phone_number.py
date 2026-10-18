import re

# Azərbaycan mobil operator prefikslərı (0 olmadan)
AZ_PREFIXES = {'10', '50', '51', '55', '70', '77', '99'}  # 60 (Naxtel) lazımdırsa əlavə et

# False etsən yalnız Azərbaycan nömrələri qəbul olunar
ALLOW_INTERNATIONAL = True

ALLOWED_CHARS = re.compile(r'^[\d\s+\-().]+$')


def parse_phone(raw: str):
    """
    Qaytarır: (normalized, is_valid)

    Qəbul olunan Azərbaycan formatları:
        +994511234567 | 994511234567 | 051 1234567 | 0511234567 | 51 1234567 | 511234567
    Nəticə həmişə 9 rəqəmdir: 511234567

    Xarici nömrələr yalnız + (və ya 00) ilə başlayanda qəbul olunur,
    nəticə +905321234567 şəklindədir.
    """
    raw = (raw or '').strip()
    if not raw or not ALLOWED_CHARS.match(raw):
        return None, False

    has_plus = raw.startswith('+') or raw.startswith('00')
    digits = re.sub(r'\D', '', raw)
    if raw.startswith('00'):
        digits = digits[2:]

    local = None
    if digits.startswith('994'):
        if len(digits) != 12:
            return None, False
        local = digits[3:]
    elif not has_plus and len(digits) == 10 and digits.startswith('0'):
        local = digits[1:]
    elif not has_plus and len(digits) == 9:
        local = digits

    if local is not None:
        if local[:2] not in AZ_PREFIXES or len(set(local[2:])) < 2:
            return None, False
        return local, True

    if ALLOW_INTERNATIONAL and has_plus and 8 <= len(digits) <= 15 and not digits.startswith('0'):
        return '+' + digits, True

    return None, False


def normalize_az_phone(phone: str):
    """Köhnə kodla uyğunluq üçün saxlanılıb."""
    value, ok = parse_phone(phone)
    return value if ok and not value.startswith('+') else None