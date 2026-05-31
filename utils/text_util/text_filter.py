def pass_text_filter(text=None,filter=None) -> bool:
    '''
    Devolver si el texto pasa el filtro
    Los parametros deben ser strings

    filter=str,text=str
    return bool

    Ejemplo:
    filtro = '123'
    text = '312'
    Final: go = True

    filtro = '123'
    text = '312.2'
    Final: go = False
    '''
    # Diccionario de caracteres del texto, para saber si el caracter paso el filtro
    dict_text = {}

    # Bucle por caracter del texto
    number = 0
    for character_text in text:
        number += 1
        # Bucle por caracter en el filtro
        # Si el caracter del texto es igual al caracter del filtro, pasa el filtro
        go =  False
        for character_filter in filter:
            if character_text == character_filter:
                go = True

        dict_text.update( {f'{number}. {character_text}' : go} )


    # Evaluar si todos los caracteres pasaron el filtro
    go = True
    for key in dict_text.keys():
        if dict_text[key] == False:
            go = False


    return go




def ignore_text_filter(text=None, filter=None) -> str:
    '''
    Ignorar los caracteres que no esten en el filtro

    filter=str,text=str
    return str or None
    '''
    text_filter = ''
    # Bucle por caracter del texto
    for character_text in text:
        # Bucle por caracter en el filtro
        # Si el caracter del texto es igual al caracter del filtro, agergarlo al caracter del texto
        for character_filter in filter:
            if character_text == character_filter:
                text_filter += character_text

    # Devolver el valor text_filter
    if text_filter == '':
        return None
    else:
        return text_filter


def ignore_comment( text='Hola #Comentario', comment='#' ):
    '''Ignorar texto con un caracter especifico en el inicio del texto'''
    if (
        '\n' in text and
        comment in text
    ):
        # Cuando hay saltos de linea y comentarios

        text_ready = ''
        for line in text.split('\n'):
            line = ignore_comment(text=line, comment=comment)
            text_ready += f'{line}\n'

        text = text_ready[:-1]

    elif comment in text:
        # Cuando hay comentarios pero no saltos de linea

        text = text.split(comment)
        text = text[0]

    else:
        # No hay nada de comenarios
        pass

    return text



def only_the_comment( text=None, comment='#' ):
    '''Obtener solo los comentarios de un texto'''
    if (
        '\n' in text and
        comment in text
    ):
        # Cuando hay saltos de linea y comentarios

        text_ready = ''
        for line in text.split('\n'):
            line = only_the_comment(text=line, comment=comment)
            if not line == None:
                text_ready += f'{line}\n'

        return text_ready[:-1]

    elif comment in text:
        # Cuando hay comentarios pero no saltos de linea
        text = text.split(comment)
        return text[1]

    else:
        # No hay nada de comenarios
        return None



def text_or_none( text: str ) -> str | None:
    # Determinar que el texto no este vacio "". Si lo esta, devuelve None, y si no el text/string.
    if bool( text.strip() ) == True:
        return text
    else:
        return None
