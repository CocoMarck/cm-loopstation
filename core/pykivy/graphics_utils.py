def update_graphics(parent, *args):
    '''
    Necesario para actualizar graficos, acomoda size, forza a cuadradito.
    '''
    min_size = min(parent.size)
    good_size = [ min_size, min_size ]
    parent.size = tuple(good_size)

    good_pos = [0, 0]
    good_pos[0] = parent.x + (parent.width -good_size[0]) / 2
    good_pos[1] = parent.y + (parent.height -good_size[1]) / 2
    parent.pos = tuple(good_pos)
