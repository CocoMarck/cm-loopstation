# Loopstation
from core.microphone_recorder import MicrophoneRecorder
from core.fps_sound_loopstation import FPSSoundLoopstation
from core.fps_sound_loopstation_recorder_controller import FPSSoundLoopstationRecorderController
from config.paths import SAMPLE_FILES

FPS = 20
FRAME_TIME = 1.0 / FPS

loopstation = FPSSoundLoopstation(
    fps=FPS, volume=0.05, play_beat=True, beat_play_mode='emphasis_on_first'
)
metronome = loopstation.fps_metronome
recorder_controller = FPSSoundLoopstationRecorderController(
    fps_sound_loopstation=loopstation, recorder=MicrophoneRecorder()
)
recorder_controller.record = True
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




sprite_layer = pygame.sprite.LayeredUpdates()
circle_group = pygame.sprite.Group()

CIRCLE_SIZE = TILE_SIZE*2
def create_circles(number=1):
    for x in range(0, number):
        circle = SpriteCircle(
            size=CIRCLE_SIZE,
            position=(
                GAME_SCREEN_SIZE[0]*0.5 -(CIRCLE_SIZE*number)//2,
                GAME_SCREEN_SIZE[1]*0.5 -(CIRCLE_SIZE)//2
            ), number = x
        )
        circle.rect.x += CIRCLE_SIZE*x
        sprite_layer.add( circle, layer=0 )
        circle_group.add( circle )

create_circles( number=loopstation.get_beats_per_bar()+1 )




# pygame setup
pygame.init()
screen = pygame.display.set_mode( SCREEN_SIZE, pygame.RESIZABLE)

game_screen = pygame.Surface( GAME_SCREEN_SIZE )
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    for sprite in sprite_layer.sprites():
        # Establce sprites en surf
        game_screen.blit(sprite.surf, sprite.rect)

    # flip() the display to put your work on screen
    scale_game_screen = pygame.transform.scale( game_screen, pygame.display.get_surface().get_size() )
    screen.blit(scale_game_screen, (0,0))
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS

pygame.quit()
