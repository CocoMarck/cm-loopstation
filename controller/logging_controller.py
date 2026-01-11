from core.standard_logging import StandardLogging


class LoggingController():
    def __init__(
        self, name="StandardLogging", filename: str="standard_logging", verbose: bool=True, log_level: str="debug", save_log: bool=True,
        only_the_value: bool=True
    ):
        # Log
        self.name = name
        self.filename = filename
        self.verbose = verbose
        self.log_level = log_level
        self.save_log = save_log
        self.formatted = f"%(levelname)s: {name}: %(message)s"
        self.__standard_log = StandardLogging(
            name=self.filename, verbose=self.verbose, level=self.log_level, save=self.save_log,
            formatted = self.formatted
        )
        self.__only_the_value = only_the_value


    def set_formatted(self):
        self.__standard_log.formatted_text = self.formatted
        self.__standard_log.set_formatted()

    def set_config(self):
        self.__standard_log.verbose = self.verbose
        self.__standard_log.save = self.save_log
        self.__standard_log.level_type = self.log_level
        self.__standard_log.set_level()
        self.__standard_log.set_logger()
        self.set_formatted()


    def set_or_not_config(self):
        # Establecer config de log. Si es que cambian `save_log, log_level, verbose`
        if (
            (self.verbose != self.__standard_log.verbose) or
            (self.save_log != self.__standard_log.save) or
            (self.log_level != self.__standard_log.level_type)
        ):
            self.set_config()


    def log(self, message, log_type="debug"):
        '''Log sencillo sin retornar nadota'''
        self.set_or_not_config()
        return self.__standard_log.log(
            message=message, log_type=log_type
        )

    
    def return_value( 
        self, value: bool | str | list, message: str, log_type="debug"
    ) -> (object, str, str):
        '''
        Devolver valor o texto dependiendo de atributos: verbose y return_message
        
        value, log_type, message
        '''
        self.set_or_not_config()
        
        # Mensaje log
        final_log_type, final_message= self.__standard_log.log( message=f"{message}", log_type=log_type )
        
        # Devolver mensaje y valor, o solo el valor
        if self.__only_the_value:
            return value
        else:
            return value, final_log_type, final_message
