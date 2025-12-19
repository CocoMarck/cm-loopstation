import pathlib


class ResourceLoader():
    '''
    Objeto que sirve para manejar todos los archivos del directorio `resources`. Tambien los de la ruta `base` de `resources`.
    '''
    def __init__(
        self, 
        base_dir=pathlib.Path().parent.absolute(),
        recource_dir_name='resources'
    ):
        super().__init__()
        
        self.base_dir = pathlib.Path().parent.absolute()

        self.data_dir = self.base_dir.joinpath( 'data' )
        self.config_dir = self.base_dir.joinpath( 'config' )
        self.logs_dir = self.base_dir.joinpath( 'logs' )

        self.resources_dir = self.base_dir.joinpath( 'resources' )
        self.images_dir = self.resources_dir.joinpath( 'images' )
        self.icons_dir = self.resources_dir.joinpath( 'icons' )
        
        
    def exists(self) -> bool:
        '''
        Determina si existe la ruta `resources`
        '''
        return self.resources_dir.is_dir()
        
        
    def get_base_path( self, path: str ) -> pathlib.Path:
        '''
        Obtiene desde la ruta base del programa un archivo.
        '''
        return self.base_dir.joinpath(path)


    def get_data( self, db: str ) -> pathlib.Path:
        '''
        Obtiene la ruta de las base de datos. Normalmente SQLite3
        '''
        return self.data_dir.joinpath( db )


    def get_config( self, config: str ) -> pathlib.Path:
        '''
        Obtiene la ruta de los archivos de configuracion. Pueden ser xml, json, .confg, .txt, .ini
        '''
        return self.config_dir.joinpath( config )
        

    def get_log( self, log: str) -> pathlib.Path:
        return self.logs_dir.joinpath( log )
        

    def get_file( self, path: str ) -> pathlib.Path:
        '''
        Obtiene archivo desde la ruta `base/resources`.
        '''
        return self.resources_dir.joinpath(path)


    def get_image( self, image: str ) -> pathlib.Path:
        '''
        Obtiene la ruta donde estan las imagenes.
        '''
        return self.images_dir.joinpath( image )


    def get_icon( self, icon: str ) -> pathlib.Path:
        '''
        Obtiene la ruta donde estan las imagenes.
        '''
        return self.icons_dir.joinpath( icon )
    
    
    def get_recursive_tree(self, path: object | pathlib.Path ) -> dict:
        '''
        Obtener directorio y archivos de manera recursiva. Depende del parametro `path`
        '''
        dict_path = {
            "directory" : [],
            "file" : []
        }
        for dir_or_file in path.rglob('*'):
            if dir_or_file.is_dir():
                dict_path["directory"].append( dir_or_file )
            elif dir_or_file.is_file():
                dict_path["file"].append( dir_or_file )

        return dict_path
    
    
    def get_base_tree( self ) -> dict:
        '''
        En `/` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.base_dir )
        

    def get_data_tree( self ) -> dict:
        '''
        En `data` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.data_dir )
        
        
    def get_config_tree( self ) -> dict:
        '''
        En `config` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.config_dir )
        
        
    def get_log_tree( self ) -> dict:
        '''
        En `log` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.logs_dir )


    def get_resource_tree( self ) -> dict:
        '''
        En `resources` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.resources_dir )
            

    def get_image_tree( self ) -> dict:
        '''
        En `resources/images` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.images_dir )
        
        
    def get_icon_tree( self ) -> dict:
        '''
        En `resources/icon` obtener de manera recursiva los directorios y archivos.
        '''
        return self.get_recursive_tree( self.icons_dir )