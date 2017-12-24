import random
import time
import pygame
import sys
from pprint import pprint  # noqa

FPS = 35
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = (WINDOWWIDTH - BOARDWIDTH * BOXSIZE) // 2
TOPMARGIN = WINDOWHEIGHT - BOARDHEIGHT * BOXSIZE - 5

#               R    G    B
WHITE       = (255, 255, 255)  # noqa
GRAY        = (185, 185, 185)  # noqa
BLACK       = (  0,   0,   0)  # noqa
RED         = (155,   0,   0)  # noqa
LIGHTRED    = (175,  20,  20)  # noqa
GREEN       = (  0, 155,   0)  # noqa
LIGHTGREEN  = ( 20, 175,  20)  # noqa
BLUE        = (  0,   0, 155)  # noqa
LIGHTBLUE   = ( 20,  20, 175)  # noqa
YELLOW      = (155, 155,   0)  # noqa
LIGHTYELLOW = (175, 175,  20)  # noqa
SILVER      = (188, 198, 204)  # noqa

BORDERCOLOR = SILVER
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS = (BLUE, GREEN, RED, YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS)  # Each color must have a light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

SHAPES = {  # 7 Shapes: S Z I O J L T
    'S': [['.....',
           '.....',
           '..OO.',
           '.OO..',
           '.....'],
          ['.....',
           '..O..',
           '..OO.',
           '...O.',
           '.....']],
    'Z': [['.....',
           '.....',
           '.OO..',
           '..OO.',
           '.....'],
          ['.....',
           '..O..',
           '.OO..',
           '.O...',
           '.....']],
    'I': [['..O..',
           '..O..',
           '..O..',
           '..O..',
           '.....'],
          ['.....',
           '.....',
           'OOOO.',
           '.....',
           '.....']],
    'O': [['.....',
           '.....',
           '.OO..',
           '.OO..',
           '.....']],
    'J': [['.....',
           '.O...',
           '.OOO.',
           '.....',
           '.....'],
          ['.....',
           '..OO.',
           '..O..',
           '..O..',
           '.....'],
          ['.....',
           '.....',
           '.OOO.',
           '...O.',
           '.....'],
          ['.....',
           '..O..',
           '..O..',
           '.OO..',
           '.....']],
    'L': [['.....',
           '...O.',
           '.OOO.',
           '.....',
           '.....'],
          ['.....',
           '..O..',
           '..O..',
           '..OO.',
           '.....'],
          ['.....',
           '.....',
           '.OOO.',
           '.O...',
           '.....'],
          ['.....',
           '..OO.',
           '...O.',
           '...O.',
           '.....']],
    'T': [['.....',
           '..O..',
           '.OOO.',
           '.....',
           '.....'],
          ['.....',
           '..O..',
           '..OO.',
           '..O..',
           '.....'],
          ['.....',
           '.....',
           '.OOO.',
           '..O..',
           '.....'],
          ['.....',
           '..O..',
           '.OO..',
           '..O..',
           '.....']]}


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    showTextScreen('Tetromino')
    while True:  # Game Loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('tetrisb.mid')
        else:
            pygame.mixer.music.load('tetrisc.mid')
        pygame.mixer.music.play(-1, 0.0)
        runGame()
        pygame.mixer.music.stop()
        showTextScreen('Game Over')


def runGame():
    # Set up variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False  # Note: There is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()

    while True:  # Main Game Loop
        if not fallingPiece:
            # No falling piece is in play, so start a new piece at the top
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            lastFallTime = time.time()  # Reset lastFallTime

            if not isValidPosition(board, fallingPiece):
                return  # Can't fit a new piece on the board, so game over

        checkForQuit()
        for event in pygame.event.get():  # Event Handling Loop
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    # Pause the game
                    DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused')  # Pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    movingLeft = False
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    movingRight = False
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    movingDown = False

            elif event.type == pygame.KEYDOWN:
                # Moving the block sideways
                if (event.key in [pygame.K_LEFT, pygame.K_a] and
                        isValidPosition(board, fallingPiece, adjX=-1)):
                    fallingPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    lastMoveSidewaysTime = time.time()
                elif (event.key in [pygame.K_RIGHT, pygame.K_d] and
                        isValidPosition(board, fallingPiece, adjX=1)):
                    fallingPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    lastMoveSidewaysTime = time.time()

                # Rotating the block (if there is room to rotate)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    r0 = fallingPiece['rotation']
                    fallingPiece['rotation'] = (
                        (r0 + 1) % len(SHAPES[fallingPiece['shape']]))
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = r0
                elif event.key == pygame.K_q:  # Rotating the other way
                    r0 = fallingPiece['rotation']
                    fallingPiece['rotation'] = (
                        (r0 - 1) % len(SHAPES[fallingPiece['shape']]))
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = r0

                # Making the block fall faster with the down key
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()
                # Move the current block all the way down
                elif event.key == pygame.K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1
                # Cheat, by changing next piece to I
                elif event.key == pygame.K_c:
                    nextPiece = getNewPiece('I')

        # Handle moving the block because of user input
        if ((movingLeft or movingRight) and
                time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ):
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
            lastMoveSidewaysTime = time.time()
        if all((movingDown, time.time() - lastMoveDownTime > MOVEDOWNFREQ,
                isValidPosition(board, fallingPiece, adjY=1))):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # Let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # See if the piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # Falling piece has landed; set it on the board
                addToBoard(board, fallingPiece)
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
            else:
                # Piece did not land; just move the block down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece:
            drawPiece(fallingPiece)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through even queue looking of a KEYUP event
    # Grab KEYDOWN events to remove them from the event queue
    checkForQuit()

    for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP]):
        if event.type == pygame.KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    # This displays large text in the center of the screen until a key press
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (WINDOWWIDTH // 2 - 3, WINDOWHEIGHT // 2 - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.',
                                              BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while not checkForKeyPress():
        pygame.display.update()
        FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get(pygame.QUIT):  # Get all the QUIT events
        terminate()  # Terminate if any QUIT events are present
    for event in pygame.event.get(pygame.KEYUP):  # Get all the KEYUP events
        if event.key == pygame.K_ESCAPE:
            terminate()  # Terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # Put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on,
    # and how many seconds pass until a falling piece falls one space
    level = score // 10 + 1
    fallFreq = 0.27 - level * 0.02
    return level, fallFreq


def getNewPiece(shape=None):
    # Return a random new piece in a random rotation and color
    if not shape:
        shape = random.choice(list(SHAPES.keys()))
    newPiece = {
        'shape': shape,
        'rotation': random.randint(0, len(SHAPES[shape]) - 1),
        'x': BOARDWIDTH // 2 - TEMPLATEWIDTH // 2,
        'y': -2,  # Start it above the board (i.e. less than 0)
        'color': random.randint(0, len(COLORS)-1)}
    return newPiece


def addToBoard(board, piece):
    # Fill in the board based on the piece's location, shape and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if SHAPES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def getBlankBoard():
    # Create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if (isAboveBoard or
                    SHAPES[piece['shape']][piece['rotation']][y][x] == BLANK):
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True


def isCompleteLine(board, y):
    # Return True if the line is filled with boxes with no gaps
    return all(board[x][y] != BLANK for x in range(BOARDWIDTH))


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them
    # down, and return the number of complete lines
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1  # Start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY - 1]
            # Set the very top line to blank
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same;
            # this is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # Move on to check next row up
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to
    # xy coordinates of the location on the screen
    return XMARGIN + boxx * BOXSIZE, TOPMARGIN + boxy * BOXSIZE


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # Draw a single box (each Tetromino piece has four boxes)
    # at xy coordinates on the board, or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece)
    if color == BLANK:
        return
    if not pixelx and not pixely:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # Draw the border around the board
    pygame.draw.rect(
            DISPLAYSURF, BORDERCOLOR,
            (XMARGIN - 3, TOPMARGIN - 7, BOARDWIDTH * BOXSIZE + 8,
             BOARDHEIGHT * BOXSIZE + 8), 5)
    # Fill the background of the board
    pygame.draw.rect(
        DISPLAYSURF, BGCOLOR,
        (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # Draw the indivitudal boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # Draw the score text
    scoreSurf = BASICFONT.render(f'Score: {score}', True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # Draw the level text
    levelSurf = BASICFONT.render(f'Level: {level}', True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = SHAPES[piece['shape']][piece['rotation']]
    if not pixelx and not pixely:
        # If pixelx & pixely haven't been specified, use the location stored
        # in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # Draw each of the blocks that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'],
                        pixelx + x * BOXSIZE, pixely + y * BOXSIZE)


def drawNextPiece(piece):
    # Draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # Draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH - 120, pixely=100)


if __name__ == '__main__':
    main()
