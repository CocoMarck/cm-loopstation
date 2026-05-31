import os
import platform
import subprocess
from .text_util import (
    read_text,
    ignore_comment,
    separe_text
)
# Importar ruta de archivo de comando de ejecucion
from .config.system_util_config import terminal_run


def get_system():
    '''Para obtener el sistema operativo utilizado'''

    system = platform.system()
    if system == 'Linux':
        return 'linux'
    elif system == 'Windows':
        return 'win'
    else:
        return 'linux'


system=get_system()


def clean_screen():
    '''Limpiar la texto de la terminal'''

    if system == 'linux':
        os.system('clear')
    elif system == 'win':
        os.system('cls')
    else:
        os.system('clear')


def run_command(
    cmd='echo', open_new_terminal=True,
    text_input='Press ENTER to continue'
):
    '''Se encarga de abrir una consola/terminal y ejecutar un comando especificado'''
    # Establecer que el comando solicitado, no tenga saltos de linea.
    # Y si tiene seran reemplzandolos por un espacio
    cmd.replace('\n', ' ')
    
    # Verificar el sistema operativo utilizado
    if system == 'linux':
        # Establecer que el string sera una comilla simple
        # Y que el comando al terminar tendra una pausa tipo input, y despues se cerrara.
        string = "'"
    
    elif system == 'win':
        # Establecer que el string sera una comilla doble
        # Y que el comando al terminar tendra una pausa tipo input, y despues se cerrara.
        string = '"'
        
    cmd = cmd.replace("'", '"')
    
    # Si queire abrir una nueva terminal
    if open_new_terminal == True:

        # Abrir una terminal nueva
        if system == 'linux':            
            cmd = (
                cmd + '; '
                f'read -rsp $"{text_input}..." -n 1 key; exit'
            )
        elif system == 'win':
            cmd = (
                cmd + " & pause"
            )

        text_terminal = ignore_comment(
            text=read_text(
                terminal_run,
                'ModeText'
            ),
            comment='#'
        )
        text_terminal = separe_text(
            text=text_terminal,
            text_separe='='
        )
        text_terminal = text_terminal[system]
        
        cmd = f'{text_terminal} {string}{cmd}{string}'
        print(cmd)
        os.system(cmd)

    else:
        # Hacer todo desde la misma terminal/programa
        os.system(cmd)
        input(f'{text_input}...')




def command_output( command: str ):
    '''
    Devuelve la salida de un comando.
    '''
    return subprocess.getoutput( command )
    
    
    

def show_file(glob=None):
    '''Muestra los archivos existentes.'''

    if type(glob) is str:
        glob = f' {glob}'
    else:
        glob = ''

    if system == 'win':
        return command_output(f'dir{glob}')
    else:
        return command_output(f'ls{glob}')



    
def view_echo(text=None):
    '''
    Para obtener las funciones de echo, sirve para obtener el resultado de las variables existentes del sistema operativo
    '''
    if (
        system == 'linux' or
        system == 'win'
    ):
        if type(text) is str:
            text = command_output( f'echo {text}' ).replace('\n', '')
        else:
            pass
        
    else:
        pass

    return text




def get_display_resolution() -> list:
    '''Retorna la resolucion del sistema'''
    if system == 'win':
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    elif system == 'linux':
        from screeninfo import get_monitors
        for monitor in get_monitors():
            width, height = monitor.width, monitor.height
    return [width, height]