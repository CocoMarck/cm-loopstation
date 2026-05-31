from pathlib import Path as pathlib

def read_text(
        file_and_path='', option='ModeList', encoding="utf-8"
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


def separe_text(
    text='variable=Valor', text_separe='='
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
