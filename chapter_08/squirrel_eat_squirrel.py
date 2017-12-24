import random
import sys
import time
import math
import pygame
from pygame.locals import *  # noqa: F403

FPS = 30
WINWIDTH = 640
WINHEIGHT = 480
HALF_WINWIDTH = WINWIDTH // 2
HALF_WINHEIGHT = WINHEIGHT // 2

GRASSCOLOR = (24, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

CAMERASLACK = 90      # How far from center the squirrel moves before camera
MOVERATE = 9          # How fast the player moves
BOUNCERATE = 6        # How fast the player bounces (larger is slower)
BOUNCEHEIGHT = 30     # How high the player bounces
STARTSIZE = 25        # How big the player starts off
WINSIZE = 300         # How big the player needs to be to win
INVULNTIME = 2        # How long the player is invulnerable after hit (sec)
GAMEOVERTIME = 4      # How long the "game over" text stays on screen (sec)
MAXHEALTH = 3         # How much health the player starts with

NUMGRASS = 80         # Number of grass objects in the active area
NUMSQUIRRELS = 30     # Number of squirrels in the active area
SQUIRRELMINSPEED = 3  # Slowest squirrel speed
SQUIRRELMAXSPEED = 7  # Fastest squirrel speed
DIRCHANGEFREQ = 2     # % chance of direction change per frame
LEFT = 'left'
RIGHT = 'right'

'''
This progam has three data structures to represent the player, enemy squirrels,
and grass background objects. The data structures are dictionaries with the
following keys:

Keys used by all three data structures:
    'x' - The left edge coordinate of the object in the game world (not a pixel
          coordinate on the screen)
    'y' - The top edge coordinate of the object in the game world (not a pixel
          coordinate on the screen)
    'rect' - The pygame.Rect object representing where on the screen the object
             is located
    'surface' - The pygame.Surface object that stores the image of the squirrel
                which will be drawn to the screen
    'facing' - Either set to LEFT or RIGHT; stores which direction the player
               is facing
    'size' - The width and height of the player in pixels (the width and height
             are always the same)
    'health' - An integer showing how many more times the player can be hit by
               a larger squirrel before dying
    'surface' - The pygame.Surface object that stores the image of the squirrel
                which will be drawn to the screen
    'movex' - How many pixels per frame the squirrel moves horizontally; a
              negative integer is moving to the left, a positive to the right
    'movey' - How many pixels per frame the squirrel moves vertically; a
              negative integer is moving up, a positive moving down
    'width' - The width of the squirrel's image, in pixels
    'height' - The height of the squirrel's image, in pixels
    'bounce' - Represents at what point in a bounce the player is. 0 means
               standing (no bounce, op to BOUNCERATE (the completion of the
               bounce)
    'bouncerate' - How quickly the squirrel bounces; lower is quicker
    'bounceheight' - How high (in pixels) the squirrel bounces

Grass data structure keys:
    'grassImage' - An integer that refers to the index of the pygame.Surface
                   object in GRASSIMAGES used for this grass object
'''


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, \
           GRASSIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Squirrel Eat Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # Load the image files
    L_SQUIR_IMG = pygame.image.load('squirrel.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = [pygame.image.load(f'grass{i}.png') for i in range(1, 5)]

    while True:
        runGame()


def runGame():
    # Set up variables for the start of a new game
    invulnerableMode = False   # If the player is invulnerable
    invulnerableStartTime = 0  # Time the player became invulnerable
    gameOverMode = False       # If the player has lost
    gameOverStartTime = 0      # Time the player lost
    winMode = False            # If the player has won

    # Create the surfaces to hold game text
    gameOverSurf = BASICFONT.render('Game Over', True, WHITE)
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf = BASICFONT.render(
        'You have achieved OMEGA SQUIRREL!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # cameraz and cameray are where the middle of the camera view is
    camerax = 0
    cameray = 0

    grassObjs = []     # Stores all the grass objects in the game
    squirrelObjs = []  # Stores all the non-player squirrel objects
    # Stores the player object:
    playerObj = {
        'surface': pygame.transform.scale(
            L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
        'facing': LEFT,
        'size': STARTSIZE,
        'x': HALF_WINWIDTH,
        'y': HALF_WINHEIGHT,
        'bounce': 0,
        'health': MAXHEALTH}

    moveLeft, moveRight, moveUp, moveDown = [False] * 4

    # Start off with some random grass images on the screen
    for i in range(10):
        grassObjs.append(makeNewGrass(camerax, cameray))
        grassObjs[i]['x'] = random.randint(0, WINWIDTH)
        grassObjs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:  # Main game loop
        # Check if we should turn off invulnerability
        if invulnerableMode and (
                time.time() - invulnerableStartTime > INVULNTIME):
            invulnerableMode = False

        # Move all the squirrels
        for sObj in squirrelObjs:
            # Move the squirrel and adjust for their bounce
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0  # Reset bounce amount

            # Random chance they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = getRandomVelocity()
                sObj['movey'] = getRandomVelocity()
                sObj['surface'] = pygame.transform.scale(
                        R_SQUIR_IMG if sObj['movex'] > 0 else L_SQUIR_IMG,
                        (sObj['width'], sObj['height']))

        # Go through all the objects and see if any need to be deleted
        for i in range(len(grassObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, grassObjs[i]):
                del grassObjs[i]
        for i in range(len(squirrelObjs) - 1, -1, -1):
            if isOutsideActiveArea(camerax, cameray, squirrelObjs[i]):
                del squirrelObjs[i]

        # Add more grass & squirrels if we don't have enough
        while len(grassObjs) < NUMGRASS:
            grassObjs.append(makeNewGrass(camerax, cameray))
        while len(squirrelObjs) < NUMSQUIRRELS:
            squirrelObjs.append(makeNewSquirrel(camerax, cameray))

        # Adjust camerax and cameray if beyond the "camera slack"
        playerCenterx = playerObj['x'] + playerObj['size'] // 2
        playerCentery = playerObj['y'] + playerObj['size'] // 2
        if (camerax + HALF_WINWIDTH) - playerCenterx > CAMERASLACK:
            camerax = playerCenterx + CAMERASLACK - HALF_WINWIDTH
        elif playerCenterx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = playerCenterx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            cameray = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # Draw the green background
        DISPLAYSURF.fill(GRASSCOLOR)

        # Draw all the grass objects on the screen
        for gObj in grassObjs:
            gRect = pygame.Rect((
                gObj['x'] - camerax,
                gObj['y'] - cameray,
                gObj['width'],
                gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # Draw the other squirrels
        for sObj in squirrelObjs:
            sObj['rect'] = pygame.Rect((
                sObj['x'] - camerax,
                sObj['y'] - cameray - getBounceAmount(
                    sObj['bounce'], sObj['bouncerate'], sObj['bounceheight']),
                sObj['width'],
                sObj['height']))
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        # Draw the player squirrel
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not gameOverMode and not(invulnerableMode and flashIsOn):
            playerObj['rect'] = pygame.Rect((
                playerObj['x'] - camerax,
                playerObj['y'] - cameray - getBounceAmount(
                    playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT),
                playerObj['size'],
                playerObj['size']))
            DISPLAYSURF.blit(playerObj['surface'], playerObj['rect'])

        # Draw the health meter
        drawHealthMeter(playerObj['health'])

        for event in pygame.event.get():  # Event handling loop
            if event.type == QUIT:                    # noqa: F405
                terminate()

            elif event.type == KEYDOWN:               # noqa: F405
                if event.key in (K_UP, K_w):          # noqa: F405
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):      # noqa: F405
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):      # noqa: F405
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] == RIGHT:  # noqa: F405
                        # Change player image
                        playerObj['surface'] = pygame.transform.scale(
                                L_SQUIR_IMG,
                                tuple([playerObj['size']] * 2))
                        playerObj['facing'] = LEFT    # noqa: F405
                elif event.key in (K_RIGHT, K_d):     # noqa: F405
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] == LEFT:   # noqa: F405
                        # Change player image
                        playerObj['surface'] = pygame.transform.scale(
                                R_SQUIR_IMG,
                                tuple([playerObj['size']] * 2))
                        playerObj['facing'] = RIGHT   # noqa: F405
                elif winMode and event.key == K_r:    # noqa: F405
                    return
            elif event.type == KEYUP:                 # noqa: F405
                # Stop moving the player's squirrel
                if event.key in (K_LEFT, K_a):        # noqa: F405
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):     # noqa: F405
                    moveRight = False
                elif event.key in (K_UP, K_w):        # noqa: F405
                    moveUp = False
                elif event.key in (K_DOWN, K_s):      # noqa: F405
                    moveDown = False

                elif event.key == K_ESCAPE:           # noqa: F405
                    terminate()

        if not gameOverMode:
            # Actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
            if moveRight:
                playerObj['x'] += MOVERATE
            if moveUp:
                playerObj['y'] -= MOVERATE
            if moveDown:
                playerObj['y'] += MOVERATE

            if (any((moveLeft, moveRight, moveUp, moveDown)) or
                    playerObj['bounce'] != 0):
                playerObj['bounce'] += 1

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0  # Reset bounce amount

            # CHeck if the player has collided with any squirrels
            for i in range(len(squirrelObjs) - 1, -1, -1):
                sqObj = squirrelObjs[i]
                if 'rect' in sqObj and playerObj['rect'].colliderect(
                        sqObj['rect']):
                    # A player/squirrel collision has occurred

                    if sqObj['width'] * sqObj['height'] <= (
                            playerObj['size']**2):
                        # Player is larger and eats the squirrel
                        playerObj['size'] += int((
                                sqObj['width'] * sqObj['height'])**0.2) + 1
                        del squirrelObjs[i]

                        if playerObj['facing'] == LEFT:
                            pygame.transform.scale(
                                    L_SQUIR_IMG,
                                    tuple([playerObj['size']] * 2))
                        if playerObj['facing'] == RIGHT:
                            playerObj['surface'] = pygame.transform.scale(
                                    R_SQUIR_IMG,
                                    tuple([playerObj['size']] * 2))
                        if playerObj['size'] > WINSIZE:
                            winMode = True  # Turn on "win mode"
                    elif not invulnerableMode:
                        # Player is smaller and takes damage
                        invulnerableMode = True
                        invulnerableStartTime = time.time()
                        playerObj['health'] -= 1
                        if playerObj['health'] == 0:
                            gameOverMode = True  # Turn on "game over mode"
                            gameOverStartTime = time.time()
        else:
            # Game is over; show "game over" text
            DISPLAYSURF.blit(gameOverSurf, gameOverRect)
            if time.time() - gameOverStartTime > GAMEOVERTIME:
                return  # End the current game

        # Check if the player has won
        if winMode:
            DISPLAYSURF.blit(winSurf, winRect)
            DISPLAYSURF.blit(winSurf2, winRect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawHealthMeter(currentHealth):
    for i in range(currentHealth):  # Draw red health bars
        pygame.draw.rect(
                DISPLAYSURF, RED,
                (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):  # Draw the white outlines
        pygame.draw.rect(
                DISPLAYSURF, WHITE,
                (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce
    # Larger bounceRate means a slower bounce
    # Larger bounceHeight means a higher bounce
    # currentBounce will always be less than bounceRate
    return int(math.sin((
        math.pi / float(bounceRate)) * currentBounce) * bounceHeight)


def getRandomVelocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # Create a Rect of the camera view
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # Create a Rect object with the random coordinates and use
        # colliderect() to make sure the right edge isn't in the camera view
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def makeNewSquirrel(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(
            camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = getRandomVelocity()
    sq['movey'] = getRandomVelocity()
    if sq['movex'] < 0:  # Squirrel is facing left
        sq['surface'] = pygame.transform.scale(
                L_SQUIR_IMG, (sq['width'], sq['height']))
    else:  # Squirrel is facing right
        sq['surface'] = pygame.transform.scale(
                R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def makeNewGrass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(
            camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr


def isOutsideActiveArea(camerax, cameray, obj):
    # Return False if camerax and cameray are more than a halp-window length
    # beyond the edge of the window
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(
            boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()
