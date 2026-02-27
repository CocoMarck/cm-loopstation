from config.paths import KVSTRING_PC, KVSTRING_ANDROID
from kivy.utils import platform

kvstring_path = KVSTRING_PC
if platform == "android":
    kvstring_path = KVSTRING_ANDROID

with open(kvstring_path, 'r') as file:
    content = file.read()

kv = content
