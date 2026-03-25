from utils.text_util import in_kebab_format, PREFIX_SPACE, PREFIX_ABC, PREFIX_NUMBER, ignore_text_filter

PREFIX_TAG_NAME = PREFIX_ABC+"-"
PREFIX_LANGUAGE_CODE = PREFIX_ABC

def format_tag_name(name):
    # Kebab Case, sin numeros
    return ignore_text_filter( name.lower().replace(' ', '-'), PREFIX_TAG_NAME)

def format_language_code(code):
    # ISO 639-1
    return ignore_text_filter( code.lower(), PREFIX_LANGUAGE_CODE)
