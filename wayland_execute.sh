#!/bin/bash

echo "Forzando el uso del driver de video SDL: X11"
export SDL_VIDEODRIVER=x11
export KIVY_GL_VSYNC=0

mangohud --dlsym vblank_mode=0 python3 main.py

echo "Ejecución de Kivy finalizada."
