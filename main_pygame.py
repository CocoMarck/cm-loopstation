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
GAME_SCREEN_SIZE = (1920, 1080)
TILE_SIZE = GAME_SCREEN_SIZE[0]//32


# Example file showing a basic pygame "game loop"
import pygame

# Fuente de Texto
pygame.font.init()
FONT_NAME = "monospace"
font_normal = pygame.font.SysFont(FONT_NAME, TILE_SIZE)

# Objeto SpriteSurf
class SpriteSurf(pygame.sprite.Sprite):
    def __init__(
        self, surf=None, size=[32,32], position=[0,0], transparency=255, color="grey"
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
        self.set_color()
        self.set_position()

    def _set_surf_base(self):
        if self._SURF == None:
            self._SURF = pygame.Surface( self.size, pygame.SRCALPHA)

    def set_surf_rect(self):
        self.rect = self.surf.get_rect()

    def set_position(self):
        self.rect.topleft = self.position

    def scale_surf(self):
        if (
            self.size[0] == self._SURF.get_size()[0] and
            self.size[1] == self._SURF.get_size()[1]
        ):
            self.surf = pygame.transform.scale( self._SURF, self.size )
        self.set_surf_rect()

    def set_color(self):
        self.scale_surf()
        self.surf.fill( self.color )
        self.surf.set_alpha( self.transparency )





# Objeto circulo
class SpriteCircle(pygame.sprite.Sprite):
    def __init__(
        self, size=32, position=(0,0), color="white", number=0
    ):
        super().__init__()

        self.NUMBER = number

        self.size = (size, size)
        self.position = position
        self.color = color

        self.surf = pygame.Surface( self.size, pygame.SRCALPHA )
        pygame.draw.circle(
            self.surf, color, (size//2,size//2), size//2
        )

        self.rect = self.surf.get_rect( topleft=position )



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
class SpriteText(pygame.sprite.Sprite):
    def __init__(
        self, text="", position=(0,0), color="white", background_color=None, identifer="sprite"
    ):
        super().__init__()

        self.identifer = identifer

        self.text = text
        self.position = position
        self.color = color

        self.font_surf = None
        self.font_rect = None
        self.set_font_surf()

        self.background_surf = None
        self.background_rect = None
        self.background_color = background_color
        self.set_background_surf()

        self.surf = None
        self.rect = None
        self.set_surf()

    def set_font_surf(self):
        self.font_surf = font_normal.render(self.text, True, self.color)
        self.font_rect = self.font_surf.get_rect()

    def is_good_background_color(self):
        return (
            isinstance( self.background_color, str ) or isinstance( self.background_color, list ) or
            isinstance( self.background_color, tuple )
        )

    def set_background_surf(self):
        self.background_surf = pygame.Surface( self.font_rect.size, pygame.SRCALPHA )
        self.background_rect = self.background_surf.get_rect()
        if self.is_good_background_color():
            self.background_surf.fill( self.background_color )

    def set_surf(self):
        self.surf = pygame.Surface( (self.font_rect.size), pygame.SRCALPHA )
        self.rect = self.surf.get_rect( topleft=self.position )
        self.surf.blit( self.background_surf, (0,0) )
        self.surf.blit( self.font_surf, (0,0) )

    def set_all(self):
        '''
        Establecer todo de una
        '''
        self.set_font()
        self.set_background_color()
        self.set_sprite_surf()




# Grupos
sprite_layer = pygame.sprite.LayeredUpdates()
circle_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()

# Método, cración de circulos
CIRCLE_SIZE = TILE_SIZE*2
def create_circles(number=1):
    for x in range(0, number):
        circle = SpriteCircle(
            size=CIRCLE_SIZE,
            position=(
                GAME_SCREEN_SIZE[0]*0.5 -(CIRCLE_SIZE*number)//2,
                GAME_SCREEN_SIZE[1]*0.15 -(CIRCLE_SIZE)//2
            ), number = x
        )
        circle.rect.x += CIRCLE_SIZE*x
        sprite_layer.add( circle, layer=0 )
        circle_group.add( circle )

create_circles( number=loopstation.get_beats_per_bar()+1 )


# Método, textos
text_title = SpriteText(
    "FPS Loopstation", position=(GAME_SCREEN_SIZE[0]//2, 0)
)
text_title.rect.x -= text_title.rect.width//2
sprite_layer.add( text_title, layer=0 )
text_group.add( text_title )

# Metodo botones
button_record = SpriteText(
    "record", position=(GAME_SCREEN_SIZE[0]//2, GAME_SCREEN_SIZE[0]*0.15),
    background_color="black", identifer="record"
)
button_record.rect.x -= button_record.rect.width//2
sprite_layer.add( button_record, layer=0 )
button_group.add( button_record )

tracks_container = SpriteSurf(
    size=[GAME_SCREEN_SIZE[0], int(GAME_SCREEN_SIZE[1]*0.55)], position=[0,GAME_SCREEN_SIZE[1]*0.45]
)
sprite_layer.add( tracks_container, layer=0 )





# pygame setup
pygame.init()
screen = pygame.display.set_mode( SCREEN_SIZE, pygame.RESIZABLE)

game_screen = pygame.Surface( GAME_SCREEN_SIZE )
clock = pygame.time.Clock()
running = True

def get_screen_multiplier(screen_size=[0,0]):
    return (
        ( GAME_SCREEN_SIZE[0] / screen_size[0] ),
        ( GAME_SCREEN_SIZE[1] / screen_size[1] )
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

    # RENDER YOUR GAME HERE
    game_screen.fill("purple")

    for circle in circle_group:
        # Circulos de beats
        circle.paint_circle_by_metronome( loopstation_signals )

    for button in button_group:
        multiplier = get_screen_multiplier( current_screen_size )
        position = [ mouse_position[0]*multiplier[0], mouse_position[1]*multiplier[1] ]
        if (
            mouse_click and button.rect.collidepoint(position)
        ):
            if button.identifer == "record":
                if recorder_controller.record:
                    recorder_controller.record = False
                else:
                    recorder_controller.record = True


    for sprite in sprite_layer.sprites():
        # Establce sprites en surf
        game_screen.blit(sprite.surf, sprite.rect)

    # flip() the display to put your work on screen
    scale_game_screen = pygame.transform.scale( game_screen, current_screen_size )
    screen.blit(scale_game_screen, (0,0))
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS

pygame.quit()
