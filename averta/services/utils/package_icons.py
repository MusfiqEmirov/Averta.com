"""Package card icon SVGs (type × variant)."""

ICON_TYPES = [
    ('plane', 'Təyyarə'),
    ('hike', 'Yürüyüş'),
    ('mountain', 'Dağ'),
    ('compass', 'Kompas'),
    ('beach', 'Çimərlik'),
    ('boat', 'Gəmi'),
    ('camera', 'Fototur'),
    ('city', 'Şəhər turu'),
    ('car', 'Avtomobil turu'),
    ('tent', 'Düşərgə'),
]

ICON_VARIANTS = [
    ('1', 'Stil 1'),
    ('2', 'Stil 2'),
    ('3', 'Stil 3'),
]

TYPE_HEADER_GRADIENTS = {
    'plane': 'linear-gradient(145deg, #1a3a8f, #3b7de8)',
    'hike': 'linear-gradient(145deg, #064e3b, #10b981)',
    'mountain': 'linear-gradient(145deg, #4c1d95, #a855f7)',
    'compass': 'linear-gradient(145deg, #78350f, #f59e0b)',
    'beach': 'linear-gradient(145deg, #0e7490, #22d3ee)',
    'boat': 'linear-gradient(145deg, #164e63, #0ea5e9)',
    'camera': 'linear-gradient(145deg, #9f1239, #f43f5e)',
    'city': 'linear-gradient(145deg, #1e293b, #64748b)',
    'car': 'linear-gradient(145deg, #312e81, #6366f1)',
    'tent': 'linear-gradient(145deg, #451a03, #b45309)',
}

# viewBox 0 0 80 80 — white icons
_ICON_SVGS = {
    'plane': {
        '1': (
            '<ellipse cx="40" cy="40" rx="4.5" ry="27" fill="white"/>'
            '<path d="M35.5 36 L7 54 L7 60 L35.5 50Z" fill="white"/>'
            '<path d="M44.5 36 L73 54 L73 60 L44.5 50Z" fill="white"/>'
            '<path d="M35.5 60 L20 68 L20 72 L35.5 66Z" fill="white"/>'
            '<path d="M44.5 60 L60 68 L60 72 L44.5 66Z" fill="white"/>'
        ),
        '2': (
            '<path d="M8 44 L72 44 L68 50 L8 50Z" fill="white" opacity="0.9"/>'
            '<path d="M40 12 L48 44 L40 40 L32 44Z" fill="white"/>'
            '<circle cx="40" cy="47" r="5" fill="white"/>'
            '<path d="M22 50 L18 58 L26 54Z M58 50 L62 58 L54 54Z" fill="white"/>'
        ),
        '3': (
            '<circle cx="40" cy="40" r="28" fill="none" stroke="white" stroke-width="2" opacity="0.4"/>'
            '<path d="M40 14 L44 38 L40 34 L36 38Z" fill="white"/>'
            '<ellipse cx="40" cy="42" rx="18" ry="4" fill="white" opacity="0.85"/>'
            '<path d="M16 42 L8 48 L12 52 L24 46Z M64 42 L72 48 L68 52 L56 46Z" fill="white"/>'
        ),
    },
    'hike': {
        '1': (
            '<circle cx="52" cy="13" r="7" fill="white"/>'
            '<path d="M48 20 C42 24 38 37 36 49 L28 67 L35 69 L41 54 L46 64 L52 74 L59 72 L50 54 L54 35 Z" fill="white"/>'
            '<rect x="54" y="21" width="8" height="13" rx="2" fill="white" opacity="0.8"/>'
        ),
        '2': (
            '<path d="M38 72 L40 28 L42 72Z" stroke="white" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<circle cx="40" cy="20" r="8" fill="white"/>'
            '<path d="M40 35 L58 55 L52 58 L40 45 L28 58 L22 55Z" fill="white" opacity="0.9"/>'
        ),
        '3': (
            '<path d="M10 72 L28 40 L40 55 L52 32 L70 72Z" fill="white" opacity="0.9"/>'
            '<circle cx="58" cy="18" r="6" fill="white"/>'
            '<path d="M24 72 L32 52" stroke="white" stroke-width="3" stroke-linecap="round"/>'
        ),
    },
    'mountain': {
        '1': (
            '<path d="M2 72 L30 20 L46 44 L58 10 L78 72Z" fill="white" opacity="0.9"/>'
            '<path d="M52 10 L46 24 L58 24Z" fill="white" opacity="0.55"/>'
        ),
        '2': (
            '<path d="M8 72 L40 18 L72 72Z" fill="white"/>'
            '<path d="M32 72 L40 42 L48 72Z" fill="white" opacity="0.35"/>'
            '<circle cx="62" cy="22" r="8" fill="white" opacity="0.7"/>'
        ),
        '3': (
            '<path d="M0 72 L20 45 L35 58 L50 28 L65 50 L80 38 L80 72Z" fill="white" opacity="0.85"/>'
            '<path d="M50 28 L45 38 L55 38Z" fill="white" opacity="0.5"/>'
        ),
    },
    'compass': {
        '1': (
            '<circle cx="40" cy="40" r="33" fill="none" stroke="white" stroke-width="2.5" opacity="0.6"/>'
            '<circle cx="40" cy="40" r="4.5" fill="white"/>'
            '<polygon points="40,9 36.5,40 40,37 43.5,40" fill="white"/>'
            '<polygon points="40,71 36.5,40 40,43 43.5,40" fill="white" opacity="0.55"/>'
            '<polygon points="9,40 40,36.5 37,40 40,43.5" fill="white" opacity="0.55"/>'
            '<polygon points="71,40 40,36.5 43,40 40,43.5" fill="white" opacity="0.55"/>'
        ),
        '2': (
            '<circle cx="40" cy="40" r="30" fill="none" stroke="white" stroke-width="2"/>'
            '<path d="M40 12 L48 40 L40 48 L32 40Z" fill="white"/>'
            '<path d="M40 68 L32 40 L40 32 L48 40Z" fill="white" opacity="0.45"/>'
            '<text x="40" y="8" text-anchor="middle" fill="white" font-size="8" font-weight="bold">N</text>'
        ),
        '3': (
            '<rect x="36" y="36" width="8" height="8" fill="white" transform="rotate(45 40 40)"/>'
            '<path d="M40 8 L44 36 L40 32 L36 36Z" fill="white"/>'
            '<path d="M40 72 L36 44 L40 48 L44 44Z" fill="white" opacity="0.5"/>'
            '<circle cx="40" cy="40" r="34" fill="none" stroke="white" stroke-width="1.5" stroke-dasharray="6 4"/>'
        ),
    },
    'beach': {
        '1': (
            '<circle cx="62" cy="18" r="14" fill="white"/>'
            '<path d="M20 72 Q24 48 28 36" stroke="white" stroke-width="4" fill="none" stroke-linecap="round"/>'
            '<path d="M0 58 Q20 52 40 58 Q60 64 80 58" fill="none" stroke="white" stroke-width="3"/>'
        ),
        '2': (
            '<circle cx="58" cy="20" r="12" fill="white"/>'
            '<path d="M5 68 Q25 58 40 62 Q55 66 75 68" stroke="white" stroke-width="3" fill="none"/>'
            '<path d="M30 72 L35 50 L40 58 L45 48 L50 72Z" fill="white" opacity="0.8"/>'
        ),
        '3': (
            '<path d="M0 50 Q20 42 40 46 Q60 50 80 44 L80 72 L0 72Z" fill="white" opacity="0.35"/>'
            '<circle cx="65" cy="16" r="10" fill="white"/>'
            '<path d="M18 30 Q22 20 26 30" stroke="white" stroke-width="2.5" fill="none"/>'
        ),
    },
    'boat': {
        '1': (
            '<path d="M10 52 L15 64 L65 64 L70 52Z" fill="white"/>'
            '<line x1="40" y1="18" x2="40" y2="52" stroke="white" stroke-width="3.5"/>'
            '<path d="M40 20 L64 48 L40 48Z" fill="white" opacity="0.85"/>'
        ),
        '2': (
            '<path d="M8 58 L72 58 L68 68 L12 68Z" fill="white"/>'
            '<path d="M40 22 C55 22 62 40 40 48 C18 40 25 22 40 22Z" fill="white" opacity="0.9"/>'
            '<path d="M0 70 Q20 64 40 68 Q60 72 80 66" stroke="white" stroke-width="2" fill="none"/>'
        ),
        '3': (
            '<ellipse cx="40" cy="58" rx="32" ry="10" fill="white" opacity="0.85"/>'
            '<rect x="36" y="28" width="8" height="32" fill="white"/>'
            '<path d="M40 28 L62 50 L40 50Z" fill="white"/>'
        ),
    },
    'camera': {
        '1': (
            '<rect x="6" y="28" width="68" height="40" rx="8" fill="white"/>'
            '<circle cx="40" cy="48" r="13" fill="none" stroke="white" stroke-width="5"/>'
            '<rect x="26" y="18" width="28" height="12" rx="6" fill="white"/>'
        ),
        '2': (
            '<circle cx="40" cy="42" r="22" fill="none" stroke="white" stroke-width="4"/>'
            '<circle cx="40" cy="42" r="10" fill="white" opacity="0.5"/>'
            '<rect x="52" y="22" width="14" height="10" rx="3" fill="white"/>'
        ),
        '3': (
            '<path d="M12 32 L20 22 L60 22 L68 32 L72 68 L8 68Z" fill="white"/>'
            '<circle cx="40" cy="48" r="14" fill="none" stroke="#13357b" stroke-width="4"/>'
            '<circle cx="58" cy="30" r="4" fill="white"/>'
        ),
    },
    'city': {
        '1': (
            '<rect x="2" y="36" width="18" height="38" fill="white"/>'
            '<rect x="22" y="20" width="14" height="54" fill="white"/>'
            '<rect x="38" y="30" width="16" height="44" fill="white"/>'
            '<rect x="56" y="44" width="22" height="30" fill="white"/>'
        ),
        '2': (
            '<rect x="8" y="40" width="12" height="34" fill="white"/>'
            '<rect x="24" y="28" width="10" height="46" fill="white"/>'
            '<rect x="38" y="34" width="14" height="40" fill="white"/>'
            '<rect x="56" y="22" width="16" height="52" fill="white"/>'
            '<circle cx="64" cy="18" r="5" fill="white" opacity="0.7"/>'
        ),
        '3': (
            '<path d="M5 72 L5 45 L20 30 L35 45 L50 25 L65 40 L75 72Z" fill="white" opacity="0.9"/>'
            '<rect x="0" y="70" width="80" height="3" fill="white" opacity="0.4"/>'
        ),
    },
    'car': {
        '1': (
            '<path d="M6 44 L6 58 L74 58 L74 44 L60 44 L50 26 L30 26 L20 44Z" fill="white"/>'
            '<circle cx="22" cy="58" r="9" fill="none" stroke="white" stroke-width="4.5"/>'
            '<circle cx="58" cy="58" r="9" fill="none" stroke="white" stroke-width="4.5"/>'
        ),
        '2': (
            '<rect x="10" y="38" width="60" height="22" rx="8" fill="white"/>'
            '<rect x="22" y="30" width="36" height="14" rx="6" fill="white" opacity="0.8"/>'
            '<circle cx="24" cy="62" r="7" fill="none" stroke="white" stroke-width="3"/>'
            '<circle cx="56" cy="62" r="7" fill="none" stroke="white" stroke-width="3"/>'
        ),
        '3': (
            '<path d="M8 50 L16 34 L64 34 L72 50 L70 62 L10 62Z" fill="white"/>'
            '<line x1="8" y1="50" x2="72" y2="50" stroke="#13357b" stroke-width="2"/>'
            '<circle cx="22" cy="62" r="6" fill="white" stroke="#13357b" stroke-width="2"/>'
            '<circle cx="58" cy="62" r="6" fill="white" stroke="#13357b" stroke-width="2"/>'
        ),
    },
    'tent': {
        '1': (
            '<path d="M4 72 L40 10 L76 72Z" fill="white" opacity="0.9"/>'
            '<path d="M30 72 L40 46 L50 72Z" fill="white" opacity="0.35"/>'
        ),
        '2': (
            '<path d="M12 72 L40 24 L68 72Z" fill="white"/>'
            '<line x1="40" y1="24" x2="40" y2="72" stroke="white" stroke-width="2" opacity="0.5"/>'
            '<rect x="34" y="58" width="12" height="14" fill="white" opacity="0.6"/>'
        ),
        '3': (
            '<path d="M8 72 L28 38 L40 52 L52 32 L72 72Z" fill="white"/>'
            '<circle cx="18" cy="24" r="3" fill="white" opacity="0.6"/>'
            '<circle cx="65" cy="20" r="3" fill="white" opacity="0.6"/>'
        ),
    },
}


def get_icon_svg_markup(icon_type, icon_variant='1', css_class='pkg-card__icon'):
    icon_type = icon_type or 'plane'
    icon_variant = icon_variant or '1'
    variants = _ICON_SVGS.get(icon_type, _ICON_SVGS['plane'])
    inner = variants.get(icon_variant) or variants.get('1', '')
    return (
        f'<svg class="{css_class}" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 80 80" aria-hidden="true">{inner}</svg>'
    )


def get_icon_svg_admin(icon_type, icon_variant='1'):
    return get_icon_svg_markup(icon_type, icon_variant, css_class='')
