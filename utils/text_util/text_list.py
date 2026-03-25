from .text_constants import PREFIX_ABC


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
