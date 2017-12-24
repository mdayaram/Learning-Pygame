import random
import sys
import time
import pygame

FPS = 60
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500  # Milliseconds
FLASHDELAY = 200  # Milliseconds
BUTTONSIZE = min(WINDOWWIDTH, WINDOWHEIGHT) // 2.4
BUTTONGAPSIZE = BUTTONSIZE // 10
TIMEOUT = 4  # Seconds before game over if no button is pushed

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHT_RED = (255, 0, 0)
RED = (155, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GREEN = (0, 155, 0)
BRIGHT_BLUE = (0, 0, 255)
BLUE = (0, 0, 155)
BRIGHT_YELLOW = (255, 255, 0)
YELLOW = (155, 155, 0)
DARK_GRAY = (40, 40, 40)
bg_color = BLACK

XMARGIN = (WINDOWWIDTH - (2 * BUTTONSIZE) - BUTTONGAPSIZE) // 2
YMARGIN = (WINDOWHEIGHT - (2 * BUTTONSIZE) - BUTTONGAPSIZE) // 2

# Rect objects for each of the four buttons
B2 = (BUTTONSIZE, BUTTONSIZE)  # Shorthand for same arguments in every Rect
YELLOW_RECT = pygame.Rect(XMARGIN, YMARGIN, *B2)
BLUE_RECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, *B2)
RED_RECT = pygame.Rect(XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, *B2)
GREEN_RECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE,
                         YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, *B2)


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode(
            (WINDOWWIDTH, WINDOWHEIGHT))  # , pygame.FULLSCREEN)
    pygame.display.set_caption('Simulate')

    BASICFONT = pygame.font.Font(
            'freesansbold.ttf', WINDOWWIDTH * WINDOWHEIGHT // 19200)

    m = 'Match the pattern by clicking on the button or using the QWAS keys.'
    infoSurf = BASICFONT.render(m, 1, DARK_GRAY)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT - 25)

    # Load the sound files
    BEEP = {i: pygame.mixer.Sound(
        'beep{}.ogg'.format(i)) for i in range(1, 5)}

    # Initialize some variables for a new game
    pattern = []       # Pattern of colors
    currentStep = 0    # Color the player must push next
    lastClickTime = 0  # Timestamp of the player's last button push
    score = 0
    # False -> Pattern is playing, True -> Waiting for player to click button
    waitingForInput = False

    while True:  # Main game loop
        clickedButton = None  # Button clicked (e.g. YELLOW/RED/GREEN/BLUE)
        DISPLAYSURF.fill(bg_color)
        drawButtons()

        scoreSurf = BASICFONT.render('Score: {}'.format(score), 1, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 100, 10)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        DISPLAYSURF.blit(infoSurf, infoRect)

        checkForQuit()
        for event in pygame.event.get():  # Event handling loop
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clickedButton = getButtonClicked(mousex, mousey)
            elif event.type == pygame.KEYDOWN:
                keycolor = {pygame.K_q: YELLOW, pygame.K_w: BLUE,
                            pygame.K_a: RED, pygame.K_s: GREEN}
                if event.key in keycolor:
                    clickedButton = keycolor[event.key]

        if not waitingForInput:
            # Play the pattern
            pygame.display.update()
            pygame.time.wait(1000)
            pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
            for button in pattern:
                flashButtonAnimation(button)
                pygame.time.wait(FLASHDELAY)
            waitingForInput = True
        else:
            # Wait for the player to enter buttons
            if clickedButton and clickedButton == pattern[currentStep]:
                # Pushed the correct button
                flashButtonAnimation(clickedButton)
                currentStep += 1
                lastClickTime = time.time()

                if currentStep == len(pattern):
                    # Pushed the last button in the pattern
                    changeBackgroundAnimation()
                    score += 1
                    waitingForInput = False
                    currentStep = 0  # Reset back to first step
            elif clickedButton and clickedButton != pattern[currentStep] or \
                    currentStep != 0 and \
                    time.time() - TIMEOUT > lastClickTime:
                # Pushed the incorrect button, or has timed out
                gameOverAnimation()
                # Reset the variables for a new game:
                pattern = []
                currentStep = 0
                waitingForInput = False
                score = 0
                pygame.time.wait(1000)
                changeBackgroundAnimation()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(pygame.QUIT):  # Get all the QUIT events
        terminate()  # Terminate if any QUIT events are present
    for event in pygame.event.get(pygame.KEYUP):  # Get all the KEYUP events
        if event.key == pygame.K_ESCAPE:
            terminate()  # Terminate if the KEYUP event was for the ESC key
        pygame.event.post(event)  # Put the other KEYUP event objects back


def flashButtonAnimation(color, animationSpeed=50):
    attributes = {
        YELLOW: (BEEP[1], BRIGHT_YELLOW, YELLOW_RECT),
        BLUE: (BEEP[2], BRIGHT_BLUE, BLUE_RECT),
        RED: (BEEP[3], BRIGHT_RED, RED_RECT),
        GREEN: (BEEP[4], BRIGHT_GREEN, GREEN_RECT)
    }
    if color in attributes:
        sound, flashColor, rectangle = attributes[color]

    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface((BUTTONSIZE, BUTTONSIZE))
    flashSurf = flashSurf.convert_alpha()
    r, g, b = flashColor
    sound.play()
    for start, end, step in ((0, 255, 1), (255, 0, -1)):  # Animation loop
        for alpha in range(start, end, animationSpeed * step):
            checkForQuit()
            DISPLAYSURF.blit(origSurf, (0, 0))
            flashSurf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flashSurf, rectangle.topleft)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    DISPLAYSURF.blit(origSurf, (0, 0))


def drawButtons():
    buttons = ((YELLOW, YELLOW_RECT), (BLUE, BLUE_RECT),
               (RED, RED_RECT), (GREEN, GREEN_RECT))
    for button in buttons:
        pygame.draw.rect(DISPLAYSURF, *button)


def changeBackgroundAnimation(animationSpeed=40):
    global bg_color
    new_bg_color = tuple(random.randint(0, 255) for i in range(3))

    new_bg_surf = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    new_bg_surf = new_bg_surf.convert_alpha()
    for alpha in range(0, 255, animationSpeed):  # Animation loop
        checkForQuit()
        DISPLAYSURF.fill(bg_color)

        new_bg_surf.fill((*new_bg_color, alpha))
        DISPLAYSURF.blit(new_bg_surf, (0, 0))

        drawButtons()  # Redraw the buttons on top of the tint

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    bg_color = new_bg_color


def gameOverAnimation(color=WHITE, animationSpeed=50):
    # Play all beeps at once, then flash the background
    origSurf = DISPLAYSURF.copy()
    flashSurf = pygame.Surface(DISPLAYSURF.get_size())
    flashSurf = flashSurf.convert_alpha()
    for beep in BEEP.values():  # Play all four beeps at the same time
        beep.play()             # (roughly)
    for i in range(3):  # Do the flash 3 times
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            # The first iteration in this loop sets the following for loop
            # To go from 0 to 255, the second from 255 to 0
            for alpha in range(start, end, animationSpeed * step):
                # Alpha means transparency; 255 is opaque, 0 is invisible
                checkForQuit()
                flashSurf.fill((*color, alpha))
                DISPLAYSURF.blit(origSurf, (0, 0))
                DISPLAYSURF.blit(flashSurf, (0, 0))
                drawButtons()
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def getButtonClicked(x, y):
    colors = {
        YELLOW: YELLOW_RECT, BLUE: BLUE_RECT,
        RED: RED_RECT, GREEN: GREEN_RECT
    }
    for color, rect in colors.items():
        if rect.collidepoint((x, y)):
            return color


if __name__ == '__main__':
    main()
