# Buildozer compilación arm 32 bits.

Para compilar mi app kivy para android de 32 bits. Es necesario evitar al 100% el `archivo.kv`, este no lo carge el app compilado.

El `SoundLoader` en Arch 32 bits, es posible que no carge el `archivos.ogg`, por lo que lo mejor es tener puros `archivos.wav`.

Las dependencias/requirements de mi app no pueden ser muy locas, las que uso son:
```
python3,kivy,pathlib,logger
```

Nada del otro mundo, pero eso si pienso usar `pysqlite`, no se si jale.

Establecer immpliciamente en el `buildozer.spec` los requirements, y que sea para 32 bits:
```
android.arch = armeabi-v7a
```