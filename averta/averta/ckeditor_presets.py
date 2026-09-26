"""
CKEditor v4 konfiqi (django-ckeditor) — admində tam alət sırası.
DEFAULT_CONFIG əsas götürülür; toolbar genişləndirilir, Flash/WSC qəsdən çıxarılır.
"""

from copy import deepcopy

from ckeditor.configs import DEFAULT_CONFIG


def build_ckeditor_default_config():
    cfg = deepcopy(DEFAULT_CONFIG)
    cfg.update(
        {
            'toolbar': 'Full',
            'height': 400,
            'width': '100%',
            'allowedContent': True,
            'pasteFromWordPromptCleanup': False,
            'pasteFromWordRemoveFontStyles': False,
            'pasteFromWordRemoveStyles': False,
            'toolbarStartupExpanded': True,
            'toolbar_Full': [
                [
                    'Styles',
                    'Format',
                    '-',
                    'Bold',
                    'Italic',
                    'Underline',
                    'Strike',
                    'Subscript',
                    'Superscript',
                    '-',
                    'RemoveFormat',
                ],
                ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'],
                ['Find', 'Replace', '-', 'SelectAll'],
                [
                    'NumberedList',
                    'BulletedList',
                    '-',
                    'Outdent',
                    'Indent',
                    '-',
                    'Blockquote',
                    '-',
                    'HorizontalRule',
                ],
                ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
                ['Link', 'Unlink', 'Anchor'],
                ['Image', 'Table', '-', 'Smiley', 'SpecialChar'],
                ['TextColor', 'BGColor'],
                ['ShowBlocks'],
                ['Maximize'],
                ['Source'],
            ],
        }
    )
    return cfg


# Django `CKEDITOR_CONFIGS` üçün kopyalayın (`settings`-də import).
CKEDITOR_PROJECT_CONFIG = {'default': build_ckeditor_default_config()}
