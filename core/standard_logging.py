import logging
import pathlib
from utils import ResourceLoader



resource_loader = ResourceLoader()

class StandardLogging():
    def __init__( 
        self, base_path: pathlib.Path = resource_loader.logs_dir, 
        name: str = "log", verbose: bool = True, save: bool = False,
        level : str = "debug", formatted: str = "%(levelname)s: %(message)s"
    ):
        # Establecer archivos
        self.base_path = base_path
        self.name = name
        self.log_file = None
        self.set_log_file()
        
        # Establecer si se mostrara o se guardara.
        self.verbose = verbose
        self.save = save
        
        # Establecer level
        self.level_type = level.lower()
        self.level = None
        self.set_level()
        
        # Establecer formato de logs
        self.formatted_text = formatted
        self.formatted = None
        self.set_formatted()
        
        # Establecer logger
        self.logger = None
        self.set_logger()
    
    
    def set_log_file( self ):
        '''
        Establecer archivo de log
        '''
        self.log_file = self.base_path.joinpath( f"{self.name}.log" )
        
    
    def set_level( self ):
        '''
        Obtener el nivel de logger
        '''
        if self.level_type == "info":
            self.level = logging.INFO

        elif self.level_type == "warning":
            self.level = logging.WARNING

        elif self.level_type == "error":
            self.level = logging.ERROR

        elif self.level_type == "critical":
            self.level = logging.CRITICAL

        else:
            self.level = logging.DEBUG
    

    def set_formatted( self ):
        '''
        Establecer formato
        '''
        self.formatted = logging.Formatter( self.formatted_text, style="%" )
    

    def set_logger( self ):
        '''
        Establecer logger
        '''
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel( self.level )
        self.logger.propagate = False # Sin estilizar (colores y añadidos) en consola.

        # Eliminar todos los hondlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Si ambos estan false, si o si el verbose sera true.
        if (not self.save) and (not self.verbose):
            self.verbose = True
        
        # Agregar handler para mostrar en consola
        if self.verbose:
            log_handler = logging.StreamHandler()
            log_handler.setLevel( self.level )
            log_handler.setFormatter(self.formatted)
            self.logger.addHandler( log_handler )
    
        # Agregar handler para guardar
        if self.save:
            log_handler = logging.FileHandler( self.log_file, encoding="utf-8" )
            log_handler.setLevel( self.level )
            log_handler.setFormatter(self.formatted)
            self.logger.addHandler( log_handler )
    
    
    
    def log(self, message: str, log_type: str = "debug") -> (str, str):
        if log_type == "info":
            self.logger.info( message )

        elif log_type == "warning":
            self.logger.warning( message )

        elif log_type == "error":
            self.logger.error( message )

        elif log_type == "critical":
            self.logger.critical( message )

        else:
            log_type = "debug"
            self.logger.debug( message )
        
        return log_type, message
    

    def debug(self, message: str):
        return self.log(message, "debug")
    
    def info(self, message: str ):
        return self.log( message, "info" )
    
    def warning(self, message: str ):
        return self.log( message, "warning" )
        
    def error(self, message: str ):
        return self.log( message, "error" )
        
    def critical(self, message: str ):
        return self.log( message, "critical" )
