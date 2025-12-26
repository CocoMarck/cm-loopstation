# Loopstation
from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from core.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from config.paths import SAMPLE_FILES

FPS = 20
FRAME_TIME = 1.0 / FPS

# Loopstation
loopstation = FPSSoundLoopstation(
    fps=FPS, volume=0.05, play_beat=True, beat_play_mode='emphasis_on_first'
)
metronome = loopstation.fps_metronome
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=MicrophoneRecorder()
)
#recorder_controller.record = True
recorder_controller.limit_record = True
recorder_controller.record_bars = 1
#loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
#loopstation.save_track( path=SAMPLE_FILES[1], sample=True )

# Constantes
SCREEN_SIZE = (960, 540)
SCENE_SIZE = (1920, 1080)
TILE_SIZE = SCENE_SIZE[0]//32


# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode( SCREEN_SIZE, pygame.RESIZABLE)

scene = pygame.Surface( SCENE_SIZE )
clock = pygame.time.Clock()


# Fuente de Texto
pygame.font.init()
FONT_NAME = "monospace"
font_normal = pygame.font.SysFont(FONT_NAME, TILE_SIZE)


# Funciones para pygame
def invert_rgb_color( rgb ):
    '''
    Invertir color rgb.
    '''
    return [255 -rgb[0], 255 -rgb[1], 255 -rgb[2] ]

def invert_pygame_color( pcolor ):
    return invert_rgb_color( (pcolor.r, pcolor.g, pcolor.b) )


# Objeto SpriteSurf
class SpriteSurf(pygame.sprite.Sprite):
    def __init__(
        self, surf=None, size=None, position=[0,0], transparency=255, identifer="sprite-surf",
        color=None, color_flags=None
    ):
        super().__init__()
        # const
        self._TRANSPARENCY = transparency
        self._SIZE = size
        self._POSITION = position
        self._COLOR = color

        # vars
        self.size = size
        self.position = position
        self.color = color
        self.transparency = transparency

        # private
        self._SURF = surf
        self._set_surf_base()

        # atributos
        self.surf = None
        self.rect = None
        self.scale_surf()
        self.set_color( flags=color_flags )
        self.set_position()

        # Identificador
        self.identifer = identifer

    def _set_surf_base(self):
        if self._SURF == None:
            self._SURF = pygame.Surface( self.size, pygame.SRCALPHA)

    def set_surf_rect(self):
        self.rect = self.surf.get_rect()

    def set_position(self):
        self.rect.topleft = self.position

    def scale_surf(self):
        good_size = self.size != None
        if good_size:
            self.surf = pygame.Surface( self.size, pygame.SRCALPHA)
        else:
            self.surf = pygame.Surface( self._SURF.get_rect().size, pygame.SRCALPHA)
        blit_surf = self._SURF
        if good_size:
            if (
                self.size[0] == self._SURF.get_size()[0] and
                self.size[1] == self._SURF.get_size()[1]
            ):
                blit_surf = pygame.transform.scale( self._SURF, self.size )
        self.surf.blit( blit_surf, (0,0) )
        self.set_surf_rect()

    def set_transparency(self):
        self.surf.set_alpha( self.transparency )

    def good_color(self):
        return not self.color == None

    def set_color(self, flags=None):
        self.scale_surf()
        if self.good_color():
            if flags == 'BLEND_MULT':
                colorSurf = pygame.Surface( self.surf.get_size() ).convert_alpha()
                colorSurf.fill( self.color )
                self.surf.blit(colorSurf, (0,0), special_flags = pygame.BLEND_RGB_MULT)
            elif flags == 'BLEND_ADD':
                self.surf.fill( self.color, special_flags=pygame.BLEND_ADD)
            else:
                self.surf.fill( self.color )
        self.set_transparency()

    def default_color(self):
        self.color = self._COLOR

    def invert_color(self):
        if self.good_color():
            self.color = invert_pygame_color( pygame.Color( self.color ) )

    def set_default_surf(self):
        self.surf = pygame.Surface( self.rect.size, pygame.SRCALPHA)
        self.surf.blit( pygame.transform.scale( self._SURF, self.rect.size ), (0,0) )





# Objeto circulo
class SpriteCircle(SpriteSurf):
    def __init__(
        self, size=32, position=(0,0), color="white", number=0
    ):
        surf = pygame.Surface( [size, size], pygame.SRCALPHA )
        pygame.draw.circle(
            surf, color, (size//2,size//2), size//2
        )
        super().__init__(
            surf=surf, size=[size, size], position=position, transparency=255, identifer="sprite-circle", color=None
        )
        self.NUMBER = number

    def paint_circle_by_metronome(self, signals):
        if self.NUMBER == signals["metronome"]["current_beat"]:
            if signals['emphasis_of_beat']['emphasis']:
                mask = pygame.mask.from_surface( self.surf )
                self.surf = mask.to_surface(setcolor="green", unsetcolor=(0, 0, 0, 0))
            elif signals['emphasis_of_beat']['neutral']:
                mask = pygame.mask.from_surface( self.surf )
                self.surf = mask.to_surface(setcolor="red", unsetcolor=(0, 0, 0, 0))
        else:
            mask = pygame.mask.from_surface( self.surf )
            self.surf = mask.to_surface(setcolor="white", unsetcolor=(0, 0, 0, 0))


# Texto
class SpriteText( SpriteSurf ):
    def __init__(
        self, font, text="", position=(0,0), color="white", background_color=None,
        identifer="sprite-text"
    ):
        super().__init__(
            size=(1,1), position=position, color=color, identifer=identifer
        )

        # Nuevos Atributos
        self.text = text
        self.antialiasing = True
        self._font = font

        # Nuevos métodos
        self.sprite_text = None
        self.set_sprite_text()

        self.sprite_background = None
        self.background_color = background_color
        self.set_sprite_background()

        self.set_surf()
        self.rect = self.surf.get_rect( topleft=self.position )

    def set_sprite_text(self):
        self.sprite_text = SpriteSurf(
            surf=self._font.render( self.text, self.antialiasing, "white" ), color=self.color, color_flags='BLEND_MULT'
        )

    def set_sprite_background(self):
        self.sprite_background = SpriteSurf(
            size=self.sprite_text.rect.size, color=self.background_color
        )

    def set_surf(self):
        self.surf = pygame.Surface( self.sprite_text.rect.size, pygame.SRCALPHA )
        self.surf.blit( self.sprite_background.surf, (0,0) )
        self.surf.blit( self.sprite_text.surf, (0,0) )
        self.set_transparency()

    def set_all(self):
        self.set_text_surf()
        self.set_background_surf()
        self.set_surf()
        self.rect = self.surf.get_rect( topleft=self.position )


class SpriteToggleButton( SpriteText ):
    def __init__( self, **kwargs ):
        super().__init__( **kwargs )

        # Nuevos atributos
        self.pressed = False

    def change_state(self):
        if self.pressed:
            self.pressed = False
        else:
            self.pressed = True

    def change_color(self):
        if self.pressed:
            self.sprite_text.invert_color()
            self.sprite_background.invert_color()
        else:
            self.sprite_text.default_color()
            self.sprite_background.default_color()
        self.sprite_text.set_default_surf()
        self.sprite_text.set_color(flags='BLEND_MULT')
        self.sprite_background.set_color()
        self.set_surf()

    def press(self):
        self.change_state()
        self.change_color()





# Grupos
sprite_layer = pygame.sprite.LayeredUpdates()
circle_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
track_options_group = pygame.sprite.Group()

# Método, cración de circulos
CIRCLE_SIZE = TILE_SIZE*2
def create_circles(number=1):
    for x in range(0, number):
        circle = SpriteCircle(
            size=CIRCLE_SIZE,
            position=(
                SCENE_SIZE[0]*0.5 -(CIRCLE_SIZE*number)//2,
                SCENE_SIZE[1]*0.15 -(CIRCLE_SIZE)//2
            ), number = x
        )
        circle.rect.x += CIRCLE_SIZE*x
        sprite_layer.add( circle, layer=0 )
        circle_group.add( circle )

create_circles( number=loopstation.get_beats_per_bar()+1 )


# Método, textos
text_title = SpriteText(
    font=font_normal, text="FPS Loopstation", position=(SCENE_SIZE[0]//2, 0)
)
text_title.rect.x -= text_title.rect.width//2
sprite_layer.add( text_title, layer=0 )
text_group.add( text_title )

# Metodo botones
button_record = SpriteToggleButton(
    font=font_normal, text="record", position=(SCENE_SIZE[0]//2, SCENE_SIZE[0]*0.15),
    background_color="black", identifer="record"
)
button_record.rect.x -= button_record.rect.width//2
sprite_layer.add( button_record, layer=0 )
button_group.add( button_record )

tracks_container = SpriteSurf(
    size=[SCENE_SIZE[0], int(SCENE_SIZE[1]*0.55)], position=[0,SCENE_SIZE[1]*0.45], color='grey'
)
def get_track_options():
    number = 0
    track_options_group.empty()
    for track_id in loopstation.get_track_ids():
        sprite_text = SpriteText(
            font=font_normal, text=str(track_id),
            position=[tracks_container.rect.x, tracks_container.rect.y + (TILE_SIZE*number)],
            color="black"
        )
        sprite_layer.add( sprite_text, layer=0 )
        text_group.add( sprite_text )
        track_options_group.add( sprite_text )

        togglebutton_play = SpriteToggleButton(
            font=font_normal, text="play",
            position=[
                tracks_container.rect.x + sprite_text.rect.right,
                tracks_container.rect.y + (TILE_SIZE*number)
            ],
            color = "black",
            background_color = "white"
        )
        sprite_layer.add( togglebutton_play, layer=0 )
        button_group.add( togglebutton_play )
        track_options_group.add( togglebutton_play )



        number += 1




# bycle
running = True

def get_screen_multiplier(screen_size=[0,0]):
    return (
        ( SCENE_SIZE[0] / screen_size[0] ),
        ( SCENE_SIZE[1] / screen_size[1] )
    )

while running:
    current_screen_size = pygame.display.get_surface().get_size()

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    mouse_click = False
    mouse_position = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        mouse_click = event.type == pygame.MOUSEBUTTONUP

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("green")

    # Loopstation events
    loopstation_signals = loopstation.update()
    recorder_controller_signals = recorder_controller.update(
        metronome_signals=loopstation_signals['metronome']
    )
    if recorder_controller_signals["stop_record"]:
        print("wakanda")
        get_track_options()

    # RENDER YOUR GAME HERE
    scene.fill("purple")
    scene.blit( tracks_container.surf, tracks_container.rect)

    for circle in circle_group:
        # Circulos de beats
        circle.paint_circle_by_metronome( loopstation_signals )

    for button in button_group:
        multiplier = get_screen_multiplier( current_screen_size )
        position = [ mouse_position[0]*multiplier[0], mouse_position[1]*multiplier[1] ]

        is_record = button.identifer == "record"
        if recorder_controller_signals["stop_record"]:
            button.pressed = False
            button.change_color()
        if (
            mouse_click and button.rect.collidepoint(position)
        ):
            button.change_state()
            if is_record:
                recorder_controller.record = button.pressed
            button.change_color()


    for sprite in sprite_layer.sprites():
        # Establce sprites en surf
        scene.blit(sprite.surf, sprite.rect)

    # flip() the display to put your work on screen
    scale_scene = pygame.transform.scale( scene, current_screen_size )
    screen.blit(scale_scene, (0,0))
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS

pygame.quit()
