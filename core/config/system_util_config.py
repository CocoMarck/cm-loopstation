import utils

# Archivo de registro de configuraciónes
resource_obj = utils.ResourceLoader()

terminal_run = resource_obj.get_config( 'runCommand.txt' )