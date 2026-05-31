from .text_filter import ignore_text_filter
from .text_constants import PREFIX_SPACE, PREFIX_ABC, PREFIX_NUMBER

PREFIX_KEBAB_CASE = PREFIX_ABC+PREFIX_NUMBER+"-"
def in_kebab_format(text):
    '''
    Formatear texto, tipo `kebab-case`
    '''
    return ignore_text_filter( text.lower().replace(' ', '-'), PREFIX_KEBAB_CASE)


def only_one_char( char=str, text=str ) -> str:
    '''
    Reemplaza cualquier secuencia de caracteres en blanco (espacios, tabulaciones, etc.) por un solo carácter especificado.

    char: str (Carácter que se va a limitar a una única aparición consecutiva)
    text: str (Texto al que se le aplicará la función)

    Retorna:
    str: Texto con una sola aparición consecutiva del carácter.
    '''
    # Divide el texto en palabras, eliminando cualquier secuencia de espacios en blanco, luego únelas con un solo espacio
    '''
    Ejemplo:
    char = '_'
    text = 'hola, hd n n n Palabra'
    text.split() hace:
    [ 'hola,', 'hd', 'n, 'n', 'n', 'Palabra']

    char.join( text.split() ) hace:
    'hola_hd_n_n_n_Palabra'
    '''
    return char.join(text.split())
