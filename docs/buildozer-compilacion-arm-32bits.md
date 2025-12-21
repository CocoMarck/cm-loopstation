# Buildozer compilación arm 32 bits.

Para compilar mi app kivy para android de 32 bits. Es necesario evitar al 100% el `archivo.kv`, este no lo carga el app compilado.

El `SoundLoader` en arch 32 bits, es posible que no carge el `archivos.ogg`, por lo que lo mejor es tener puros `archivos.wav`.

Las dependencias/requirements de mi app no pueden ser muy locas, las que uso son:
```
python3,kivy,pathlib,logger
```

Nada del otro mundo, pero eso si pienso usar `pysqlite`, no se si jale.

## El `buildozer.spec`
Establecer immpliciamente en el `buildozer.spec` los requirements:
```
requirements = python3,kivy,pathlib,logger
```

Que sea para 32 bits:
```
android.arch = armeabi-v7a
```
O para las dos arquitecturas:
```
arm64-v8a
```

Tambien idicar en `orientation`; Para que jale en vertical y horizontal:
```
orientation = landscape, portrait, portrait-reverse or landscape-reverse
```
Los que digan `reverse` se pueden evitar, es por si tienes alrevez el celu.
