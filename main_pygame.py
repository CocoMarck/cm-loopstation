# Example file showing a basic pygame "game loop"
import pygame

# Loopstation
from core.fps_loopstation import FPSLoopstation
from config.paths import SAMPLE_FILES

FPS = 20
FRAME_TIME = 1.0 / FPS

loopstation = FPSLoopstation()
loopstation.fps = FPS
loopstation.volume = 0.1
#loopstation.save_track( path=SAMPLE_FILES[0], sample=True )
#loopstation.save_track( path=SAMPLE_FILES[1], sample=True )
loopstation.play_beat = True
loopstation.recording = True
loopstation.recorder_limit_in_bars = 1
loopstation.limit_recording = True
loopstation.timer_in_seconds = 10
loopstation.update_all_data()

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE
    loopstation.looping()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS to 60

pygame.quit()
