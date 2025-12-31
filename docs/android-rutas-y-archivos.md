# Android rutas y permisos

Android tiene modulos/libs python, para poder hacer apps escritas en python. Veremos como usar algunas.

# `android.storage`
En android tenemos rutas y permisos para acceder en esas rutas, lo mejor es usar las rutas que Android recominda usar, de lo contrario tendremos problemas con los permisos:
```python
from android.storage import app_storage_path
ANDROID_MUSIC_PATH = pathlib.Path(app_storage_path())
```

Para guardar tus archivitos, usa rutas `android.storage`, la mera neta, pioriza usar nomas `app_storage_path`, ni digo a que path hace referencia, es explícito.

# `android.permissions`
En la construccion de nuestra app, añadimos los permisos necesarios. Aca por ejemplo, se agregaron de una los permisos de grabar audio de microfono, leer y escribir archivos externos (externos a la app).
```python
    def build(self):
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
```





