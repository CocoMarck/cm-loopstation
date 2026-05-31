from config.paths import KVSTRING_PC, KVSTRING_ANDROID, KVSTRING
from kivy.utils import platform

#kvstring_path = KVSTRING_PC
#if platform == "android":
    #kvstring_path = KVSTRING_ANDROID
kvstring_path = KVSTRING

with open(kvstring_path, 'r') as file:
    content = file.read()

kv = content
