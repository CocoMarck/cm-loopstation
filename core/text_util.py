from pathlib import Path as pathlib




PREFIX_ABC = 'abcdefghijklmnñopqrstuvwxyz'
PREFIX_NUMBER = '1234567890'
PREFIX_SPACE = ' \n'


def read_text(
        file_and_path='',
        option='ModeList',
        encoding="utf-8"
    ):
    '''Lee un archivo de texto y devuelve la información en una lista, variable o diccionario.'''
    
    #text_final = None
    
    if pathlib(file_and_path).exists():
        with open(file_and_path, 'r', encoding=encoding) as text:
            text_read = text.read()
        
        if (
            option == 'ModeTextOnly' or
            option == 'ModeText'
        ):
            text_final = ''
            for line in text_read:
                text_final += line
            
            if option == 'ModeTextOnly':
                text_final = text_final.replace('\n', ' ')
            
            return text_final
        
        elif option == 'ModeDict':
            text_final = {}
            text_read = read_text(
                file_and_path=file_and_path, 
                option='ModeText'
            )
            number = 0
            for line in text_read.splitlines():
                number += 1
                text_final.update( {number : line} )

            return text_final
        
        elif option == 'ModeList':
            text_final = []
            for line in text_read.splitlines():
                text_final.append(line)
            return text_final
        
        else:
            return text_read
    
    else:
        return None


def ignore_comment(
    text='Hola #Comentario',
    comment='#'
):
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


def separe_text(
    text='variable=Valor',
    text_separe='='
):
    '''Para separar el texto en 2 y almacenarlo en un diccionario'''

    text_dict = {}
    if (
        '\n' in text and
        text_separe in text
    ):
        # Cuando hay saltos de linea y separador
        for line in text.split('\n'):
            line = separe_text(text=line, text_separe=text_separe)
            for key in line.keys():
                text_dict.update( {key : line[key]} )

    elif text_separe in text:
        # Cuando solo hay separador
        text = text.split(text_separe)
        text_dict.update( {text[0] : text[1]} )
    else:
        pass
    
    return text_dict




def only_the_comment(
    text=None,
    comment='#'
):
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




def abc_list(list=None):
    # Ordenar cada letra del abecedario en un dicionario
    abc = PREFIX_ABC
    dict_abc = {}
    number = 0
    for character in abc:
        dict_abc.update( {character : number} )
        number += 1
    #number -= 1

    # Ordenar en un dicionario
    # Al detercar con que letra enpieza el item de la lista, ingorar cualquier caracter que no sea abc.
    # Posicionar cualquier string sin abs a z.
    dict_ready = {}
    for key in dict_abc.keys():
        dict_ready.update( {dict_abc[key]: [] } )

    # Filtros necesarios
    for text in list:
        # Filtrar texto
        text_filter = ignore_text_filter( text=text.replace(' ', '').lower(), filter=abc )
        if text_filter == None:
            pass_filter = False
        else:
            pass_filter = pass_text_filter( text=text_filter, filter=abc )

        # Si pasa el filtro
        if pass_filter == True:
            for key in dict_abc.keys():
                if text_filter.startswith(key):
                    dict_ready[ dict_abc[key] ].append( text )
        elif pass_filter == False:
            dict_ready[ dict_abc['z'] ].append(text)


    # Ordenar en base al dicionario ordenado
    list_ready = []
    for index in range(0, number):
        for key in dict_ready.keys():
            if key == index:
                if not dict_ready[key] == []:
                    for item in dict_ready[key]:
                        list_ready.append( item )

    # Devolver la lista ordenada
    return list_ready




def not_repeat_item( list=None ) -> list:
    '''
    Elimina los items repetidos en una lista.
    '''
    new_list = []
    for item in list:
        if new_list == []:
            new_list.append( item )

        go = True
        for i in new_list:
            if i == item:
                go = False

        if go == True:
            new_list.append( item )

    return new_list
    
    
def text_or_none( text: str ) -> str | None:
    # Determinar que el texto no este vacio "". Si lo esta, devuelve None, y si no el text/string.
    return_value = None
    if isinstance(text, str):
        if bool( text.strip() ) == True:
            return_value = text

    return return_value