import random

RGB_MAX_VALUE = 255
RGB_MIN_VALUE = 0

def number_to_rgb_value( number ):
    '''
    Normalizar valores numericos
    '''
    if number > RGB_MAX_VALUE:
        return RGB_MAX_VALUE
    elif number < RGB_MIN_VALUE:
        return RGB_MIN_VALUE
    else:
        return int(number)

def get_rgb( r, g, b ):
    '''
    Obtener color rgb, por medio de una lista, y con numeros normalizados
    '''
    return [
        number_to_rgb_value(r), number_to_rgb_value(g), number_to_rgb_value(b)
    ]

def get_rgba( r, g, b, a ):
    '''
    Obtener color rgba, por medio de una lista, y con numeros normalizados
    '''
    rgb = get_rgb( r, g, b )
    return [
        rgb[0], rgb[1], rgb[2], number_to_rgb_value(a)
    ]

def invert_rgb_value( value ):
    '''
    Invertir numero. NO NORMALIZR, seria redundante. Asumir valores buenos.
    '''
    return RGB_MAX_VALUE -value

def invert_rgb( rgb ):
    r, g, b = rgb
    return [ invert_rgb_value(r), invert_rgb_value(g), invert_rgb_value(b) ]

def invert_rgba( rgba ):
    r, g, b, a = rgba
    ir, ig, ib = invert_rgb( [r, g, b] )
    return [ ir, ig, ib, a ]

def normalize_rgb_value( value ):
    if value > 0:
        return float(value / RGB_MAX_VALUE)
    else:
        return float(0)

def rgb_to_normalized( rgb ):
    r, g, b = rgb
    return [
        normalize_rgb_value(r), normalize_rgb_value(g), normalize_rgb_value(b)
    ]

def rgba_to_normalized( rgba ):
    r, g, b, a = rgba
    nr, ng, nb = rgb_to_normalized( [r,g,b] )
    return [
        nr, ng, nb, normalize_rgb_value(a)
    ]

def scale_rgb( rgb, multiplier=1 ):
    r, g, b = rgb
    return get_rgb( r*multiplier, g*multiplier, b*multiplier )

def scale_rgba( rgba, multiplier=1):
    r, g, b, a = rgba
    mr, mg, mb = scale_rgb( [r, g, b], multiplier )
    return [mr, mg, mb, a]

def random_rgb():
    r = random.randint(RGB_MIN_VALUE, RGB_MAX_VALUE)
    g = random.randint(RGB_MIN_VALUE, RGB_MAX_VALUE)
    b = random.randint(RGB_MIN_VALUE, RGB_MAX_VALUE)
    return get_rgb(r, g, b)

def random_rgba():
    rr, rg, rb = random_rgb()
    return [rr, rg, rb, RGB_MAX_VALUE]


def is_the_rgb_color_bright( rgb ):
    bright_values = []
    for value in rgb:
        bright_values.append( value >= RGB_MAX_VALUE//2 )
    count_bright_values = 0
    for value in bright_values:
        if value:
            count_bright_values += 1
    return count_bright_values >= 2


def is_the_rgba_color_bright( rgba ):
    r, g, b, a = rgba
    return is_the_rgb_color_bright( [r,g,b] )
