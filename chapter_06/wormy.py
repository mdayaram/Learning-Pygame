import random
import pygame
import sys
from pprint import pprint  # noqa

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, \
       'Window width must be a multiple of cell size.'
assert WINDOWHEIGHT % CELLSIZE == 0, \
       'Window height must be a multiple of cell size.'
CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# Colors      R    G    B
WHITE     = (255, 255, 255)  # noqa
BLACK     = (  0,   0,   0)  # noqa
RED       = (255,   0,   0)  # noqa
GREEN     = (  0, 255,   0)  # noqa
DARKGREEN = (  0, 155,   0)  # noqa
DARKGRAY  = ( 40,  40,  40)  # noqa
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
directions = {
    UP: {'maps': [pygame.K_UP, pygame.K_w], 'reverse': DOWN},
    DOWN: {'maps': [pygame.K_DOWN, pygame.K_s], 'reverse': UP},
    LEFT: {'maps': [pygame.K_LEFT, pygame.K_a], 'reverse': RIGHT},
    RIGHT: {'maps': [pygame.K_RIGHT, pygame.K_d], 'reverse': LEFT}}

HEAD = 0  # Syntactic Sugar: Index of the Worm's Head


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx - i, 'y': starty} for i in range(3)]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True:  # Main Game Loop
        for event in pygame.event.get():  # Event Handling Loop
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                for d, v in directions.items():
                    if event.key in v['maps'] and direction != v['reverse']:
                        direction = d
                        break

        # Check if the worm has hit itself or the edge.
        if any([wormCoords[HEAD]['x'] not in range(CELLWIDTH),
                wormCoords[HEAD]['y'] not in range(CELLHEIGHT),
                wormCoords[HEAD] in wormCoords[1:]]):
            return  # Game Over

        # Check if the worm has eaten an apple.
        if wormCoords[HEAD] == apple:
            apple = getRandomLocation()  # Don't remove the worm's tail.
        else:
            del wormCoords[-1]           # Remove the worm's tail.

        # Move the worm by adding a segment in the direction it is moving.
        newHead = dict(wormCoords[HEAD])
        if direction == UP:
            newHead['y'] -= 1
        elif direction == DOWN:
            newHead['y'] += 1
        elif direction == LEFT:
            newHead['x'] -= 1
        elif direction == RIGHT:
            newHead['x'] += 1
        wormCoords.insert(0, newHead)

        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(pygame.QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(pygame.KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == pygame.K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # Clear Event Queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # Rotate by 3 degrees each frame.
        degrees2 += 7  # Rotate by 7 degrees each frame.


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {
        'x': random.randint(0, CELLWIDTH - 1),
        'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # Clear out any key presses in the event queue.

    while True:
        if checkForKeyPress():
            pygame.event.get()  # Clear the event queue.
            return


def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4,
                                           CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # Draw vertical lines.
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # Draw horizontal lines.
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
