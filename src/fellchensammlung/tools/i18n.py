from django.utils import translation

from fellchensammlung.models import Language, Text


def get_text_by_language(text_code, lang=None):
    if lang is None:
        language_code = translation.get_language()
        lang = Language.objects.get(languagecode=language_code)
    return Text.objects.get(text_code=text_code, language=lang, )


def get_texts_by_language(text_codes):
    language_code = translation.get_language()
    lang = Language.objects.get(languagecode=language_code)

    texts = {}
    for text_code in text_codes:
        try:
            texts[text_code] = get_text_by_language(text_code, lang)
        except Text.DoesNotExist:
            texts[text_code] = None
    return texts
