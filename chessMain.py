"""
This is our main driver file.
It is responsible for handling user input and displaying the current gameState object.
"""

import pygame as p
import chessEngine
import chessAI
from multiprocessing import Process, Queue
import sys
import asyncio
import sqlite3
import hashlib

p.init()

p.display.set_caption("Chess Engine") #how to change title

BASE_COLOUR = "Black"
HOVERING_COLOUR = "#2F2F2F"
SYSTEM_FONT = "montserrat"

WIDTH = HEIGHT = 512 #pixels
MOVE_LOG_PANEL_WIDTH = 250 #pixels
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8 #dimensions of a chessboard are 8x8
SQ_SIZE = HEIGHT // DIMENSION #size of a square
MAX_FPS = 15 #for animations later on
IMAGES = {}

"""
Initialise a global dictionary of images. This will be called exactly once in the main.
"""
def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("pieces/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: we can access an image by saying 'IMAGES["wP"]'

"""
The main function for our code, this will handle user input and updating the graphics.
"""
def main(settings):
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False) #font for move log
    gs = chessEngine.gameState() #creates a gameState object
    validMoves = gs.getValidMoves() #returns all the valid moves on the board
    moveMade = False #flag variable for when a move has been made
    animate = False #flag variable for when we should animate a move
    loadImages() #only do this once, before the while loop
    running = True
    sqSelected = () #no square is selected initially, keeps track of the last click of a user, tuple: (row, col)
    playerClicks = [] #keeps track of player clicks, two tuples: [(6, 4), (4, 4)]
    gameOver = False
    playerOne = True #true if human is playing white, false if AI is playing white
    playerTwo = settings[2] #same as above but for black
    AIThinking = False #returns if the AI is thinking of a move or not
    moveUndone = False #returns if a move has been undone or not
    moveFinderProcess = None

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo) #returns if a human is playing this turn or not
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if gameOver:
                    if END_BUTTON.checkForInput(MENU_MOUSE_POS): #if left click on end button
                        endGame(settings, gs.whiteToMove, gs.stalemate) #call endGame function
                if not gameOver:
                    location = p.mouse.get_pos() #returns (x, y) location of mouse
                    col = location[0] // SQ_SIZE #returns the corresponding column the mouse is on
                    row = location[1] // SQ_SIZE #returns the corresponding row the mouse is on
                    if sqSelected == (row, col) or col >= 8: #the user clicked the same square twice or user clicked move log
                        sqSelected = () #deselect
                        playerClicks = [] #clear playerClicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both first and second clicks
                    if len(playerClicks) == 2 and humanTurn: #after second click
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board) #creates a move object using the Move class
                        print(move.getChessNotation()) #returns the move in chess notation format in the console
                        for i in range(len(validMoves)): #loop through validMoves
                            if move == validMoves[i]: #is the move valid?
                                gs.makeMove(validMoves[i]) #makes the move
                                moveMade = True #flags the moveMade as true
                                animate = True #flags the animate as true
                                sqSelected = () #reset
                                playerClicks = [] #reset
                        if not moveMade: #if a move has not been made yet
                            playerClicks = [sqSelected] #select a different piece
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when "z" is pressed
                    gs.undoMove()
                    moveMade = True #flags the moveMade as true
                    animate = False #flags the animate as false
                    gameOver = False #flags the gameOver as false
                    if AIThinking:
                        moveFinderProcess.terminate() #stop thinking
                        AIThinking = False
                    moveUndone = True #move has been undone

                if e.key == p.K_r: #reset board when "r" is pressed
                    gs = chessEngine.gameState() #create a new gameState
                    validMoves = gs.getValidMoves() #get new valid moves
                    sqSelected = () #reset
                    playerClicks = [] #reset
                    moveMade = False #reset
                    animate = False #reset
                    gameOver = False #reset
                    if AIThinking:
                        moveFinderProcess.terminate() #stop thinking
                        AIThinking = False
                    moveUndone = False #reset

        #AI move finder logic
        if not gameOver and not humanTurn and not moveUndone: #if game isnt over and a human isnt playing this turn and a move has not been undone
            if not AIThinking:
                #set AI difficulty
                if settings[3] == "easy":
                    gs.makeMove(chessAI.findRandomMove(validMoves))
                    moveMade = True #flags the moveMade as true
                    animate = True #flags the animate as true
                elif settings[3] == "medium":
                    gs.makeMove(chessAI.findGreedyMove(gs, validMoves))
                    moveMade = True #flags the moveMade as true
                    animate = True #flags the animate as true
                elif settings[3] == "hard":
                    AIThinking = True #start thinking
                    returnQueue = Queue() #create a queue
                    moveFinderProcess = Process(target=chessAI.findBestMoveNegaMaxAlphaBeta, args=(gs, validMoves, returnQueue)) #create a process
                    moveFinderProcess.start() #call process
            
            if settings[3] == "hard":
                if not moveFinderProcess.is_alive(): #if done thinking
                    AIMove = returnQueue.get() #get the move
                    if AIMove is None: #if AIMove is equal to None
                        AIMove = chessAI.findRandomMove(validMoves) #get a random move
                    gs.makeMove(AIMove) #make the suggested move
                    moveMade = True #flags the moveMade as true
                    animate = True #flags the animate as true
                    AIThinking = False #done thinking

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock) #animate the last move in our move log
            validMoves = gs.getValidMoves() #generates a new list of valid moves whenever a move has been made
            moveMade = False #flags the moveMade back to false
            animate = False #flags the animate back to false
            moveUndone = False #flags the moveUndone back to false

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True #flags the gameOver as true
            drawEndGameText(screen, "Stalemate" if gs.stalemate else "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate") #draw end game text
            MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position
            END_BUTTON = Button(None, pos=(260, 300), text_input="END GAME", font=p.font.SysFont(SYSTEM_FONT, 45), base_colour="white", hovering_colour="red") #end button
            END_BUTTON.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            END_BUTTON.update(screen) #draw button to screen

        clock.tick(MAX_FPS)
        p.display.flip()

"""
End game function
"""
def endGame(settings, whiteToMove, stalemate):
    #update stats accordingly
    if stalemate:
        #stalemate is true
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
        userData = cur.fetchall() #grab user's data from database
        conn.close()
        userDraws = userData[0][4] + 1 #increment user's draws
        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()
        cur.execute("UPDATE userdata SET draws = ? WHERE username = ? AND password = ?", (userDraws, settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
        conn.commit() #save new statistics
        conn.close()
    else:
        if whiteToMove:
            #enemy wins
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
            userData = cur.fetchall() #grab user's data from database
            conn.close()
            userLosses = userData[0][5] + 1 #increment user's losses
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            cur.execute("UPDATE userdata SET losses = ? WHERE username = ? AND password = ?", (userLosses, settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
            conn.commit() #save new statistics
            conn.close()
        else:
            #player wins
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
            userData = cur.fetchall() #grab user's data from database
            conn.close()
            userWins = userData[0][3] + 1 #increment user's wins
            conn = sqlite3.connect("userdata.db")
            cur = conn.cursor()
            cur.execute("UPDATE userdata SET wins = ? WHERE username = ? AND password = ?", (userWins, settings[0], hashlib.sha256(settings[1].encode()).hexdigest()))
            conn.commit() #save new statistics
            conn.close()
    #send player to mainMenu()
    mainMenu(settings[0], settings[1])

"""
Highlight square selected and moves for piece selected
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != (): #if sqSelected is not empty
        r, c = sqSelected #copies what is inside of sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #check that sqSelected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE)) #create a pygame surface object
            s.set_alpha(100) #transparency value: 0 transparent -> 255 opaque
            s.fill(p.Color("yellow")) #colour value
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE)) #places the surface object onto the screen on top of the sqSelected
            #highlight moves from that square
            s.fill(p.Color("green")) #colour value
            for move in validMoves: #for every valid move
                if move.startRow == r and move.startCol == c: #if the move starts from the same position as our sqSelected
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE)) #highlight it

"""
Responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves,sqSelected) #highlights squares
    drawPieces(screen, gs.board) #draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont) #draw the move log

"""
Draw the squares on the board. The top left square is always light.
"""
def drawBoard(screen):
    global colours
    colours = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c)%2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draw the pieces on the board using the current gameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not an empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draws the move log
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT) #create rectangle object
    p.draw.rect(screen, p.Color("Black"), moveLogRect) #draw rectangle on screen
    moveLog = gs.moveLog #get move log
    moveTexts = [] #empty array
    for i in range(0, len(moveLog), 2): #loop through moveLog
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " " #add white move
        if i + 1 < len(moveLog): #if black made a move
            moveString += str(moveLog[i + 1]) + " " #add black move to text
        moveTexts.append(moveString) #add text to array
    movesPerRow = 3
    padding = 5 #set padding between text
    lineSpacing = 2 #set line spacing
    textY = padding #set height of text location
    for i in range(0, len(moveTexts), movesPerRow): #loop through move texts
        text = "" #empty string
        for j in range(movesPerRow):
            if i + j < len(moveTexts): #if in bounds
                text += moveTexts[i+j] #add text
        textObject = font.render(text, True, p.Color("White")) #create text object
        textLocation = moveLogRect.move(padding, textY) #set text location
        screen.blit(textObject, textLocation) #render move text
        textY += textObject.get_height() + lineSpacing #bring text lower next iteration

"""
Animate a move
"""
def animateMove(move, screen, board, clock):
    global colours
    dR = move.endRow - move.startRow #delta (change in) row
    dC = move.endCol - move.startCol #delta (change in) col
    framesPerSquare = 3 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare #how many frames a move will take to animate
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount) #coordinates of piece moved during animation
        drawBoard(screen) #draw board for every frame
        drawPieces(screen, board) #draw pieces for every frame
        #erase the piece moved from it's end square
        colour = colours[(move.endRow + move.endCol) % 2] #returns the colour of the end square
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE) #rectangle object
        p.draw.rect(screen, colour, endSquare) #draw end square
        #draw captured piece back
        if move.pieceCaptured != "--": #if there is a piece to draw
            if move.isEnPassantMove: #if it is an en passant move
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE) #recalculate endSquare
            screen.blit(IMAGES[move.pieceCaptured], endSquare) #draw it on the endSquare
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

"""
Draw given text on screen
"""
def drawEndGameText(screen, text):
    #background
    background = p.Rect(0, HEIGHT/2.65, WIDTH, HEIGHT/4) #rectangle object
    p.draw.rect(screen, p.Color("#333333"), background) #draw it on screen
    #text
    font = p.font.SysFont("Helvetica", 32, True, False) #create font object
    textObject = font.render(text, 0, p.Color("Black")) #render text shadow
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2) #center text
    screen.blit(textObject, textLocation) #draw the text shadow on screen
    textObject = font.render(text, 0, p.Color("White")) #render text
    screen.blit(textObject, textLocation.move(2, 2)) #draw the text on screen

"""
MENU FUNCTIONS
"""
#button class
class Button():
    def __init__(self, image, pos, text_input, font, base_colour, hovering_colour):
        self.image = image #sets image
        self.x_pos = pos[0] #sets x-position
        self.y_pos = pos[1] #sets y-position
        self.font = font #sets font
        self.base_colour, self.hovering_colour = base_colour, hovering_colour #sets base colour and hovering colour
        self.text_input = text_input #sets text input
        self.text = self.font.render(self.text_input, True, self.base_colour) #renders text
        if self.image is None: #no image
            self.image = self.text #sets image to text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) #rect object for image
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos)) #rect object for text

    #updates button
    def update(self, screen):
        if self.image is not None: #image
            screen.blit(self.image, self.rect) #place image on screen
        screen.blit(self.text, self.text_rect) #place text on screen
    
    #checks if mouse is hovering over button
    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom): #is mouse hovering over button?
            return True
        return False
    
    #changes the colour of the button if the mouse is hovering over it
    def changeColour(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom): #is mouse hovering over button?
            self.text = self.font.render(self.text_input, True, self.hovering_colour) #change colour to hovering colour
        else:
            self.text = self.font.render(self.text_input, True, self.base_colour) #change colour to base colour

#start menu function
def startMenu():
    startMenu = True #while loop flag variable
    screen.fill("White") #turn screen white

    while startMenu:
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect

        START_BUTTON = Button(None, pos=(375, 250), text_input="START", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #start button
        QUIT_BUTTON = Button(None, pos=(375, 350), text_input="QUIT", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #quit button

        screen.blit(MENU_TEXT, MENU_RECT) #draw text to screen

        for button in [START_BUTTON, QUIT_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if START_BUTTON.checkForInput(MENU_MOUSE_POS): #on start button
                    loginMenu() #send to login menu
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS): #on quit button
                    p.quit()
                    sys.exit()
        
        p.display.update()

#login menu function
def loginMenu():
    loginMenu = True #while loop flag variable
    screen.fill("White") #turn screen white

    while loginMenu:
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect

        LOGIN_BUTTON = Button(None, pos=(375, 250), text_input="LOG IN", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #log in button
        SIGNUP_BUTTON = Button(None, pos=(375, 350), text_input="SIGN UP", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #sign up button
        
        screen.blit(MENU_TEXT, MENU_RECT) #draw text to screen

        for button in [LOGIN_BUTTON, SIGNUP_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if LOGIN_BUTTON.checkForInput(MENU_MOUSE_POS): #on log in button
                    logIn() #send to log in
                if SIGNUP_BUTTON.checkForInput(MENU_MOUSE_POS): #on sign up button
                    signUp() #send to sign up
        
        p.display.update()

#log in function
def logIn():
    login = True #while loop flag variable
    response = False #response flag variable

    screen.fill("White") #turn screen white

    #initialise username input
    USERNAME_INPUT = ""
    USERNAME_INPUT_RECT = p.Rect(350, 160, 395, 75)
    USERNAME_COLOUR = BASE_COLOUR
    USERNAME_ACTIVE = False

    #initialise password input
    PASSWORD_INPUT = ""
    PASSWORD_INPUT_RECT = p.Rect(350, 260, 395, 75)
    PASSWORD_COLOUR = BASE_COLOUR
    PASSWORD_ACTIVE = False

    while login:
        screen.fill("White") #turn screen white
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect
        
        USERNAME_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("USERNAME", True, USERNAME_COLOUR) #username text
        USERNAME_RECT = USERNAME_TEXT.get_rect(center=(175, 200)) #username rect
        
        PASSWORD_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("PASSWORD", True, PASSWORD_COLOUR) #password text
        PASSWORD_RECT = PASSWORD_TEXT.get_rect(center=(175, 300)) #password rect

        ENTER_BUTTON = Button(None, pos=(375, 400), text_input="LOG IN", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #enter button

        screen.blit(MENU_TEXT, MENU_RECT) #draw title text to screen
        screen.blit(USERNAME_TEXT, USERNAME_RECT) #draw username text to screen
        screen.blit(PASSWORD_TEXT, PASSWORD_RECT) #draw password text to screen
        
        for button in [ENTER_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if ENTER_BUTTON.checkForInput(MENU_MOUSE_POS): #on enter button
                    response = asyncio.run(log_user_in(USERNAME_INPUT, PASSWORD_INPUT)) #generate response
                if USERNAME_INPUT_RECT.collidepoint(event.pos): #on username input
                    USERNAME_ACTIVE = True #select username input
                else:
                    USERNAME_ACTIVE = False #deselect username input
                if PASSWORD_INPUT_RECT.collidepoint(event.pos): #on passsword input
                    PASSWORD_ACTIVE = True #select password input
                else:
                    PASSWORD_ACTIVE = False #deselect password input
            if event.type == p.KEYDOWN: #if keyboard button press
                if USERNAME_ACTIVE == True: #if username input selected
                    if event.key == p.K_RETURN: #if return key pressed
                        pass
                    elif event.key == p.K_BACKSPACE: #if backspace key pressed
                        USERNAME_INPUT = USERNAME_INPUT[:-1] #delete last character
                    elif len(USERNAME_INPUT) >= 8: #if max length
                        pass
                    else: #otherwise
                        USERNAME_INPUT += event.unicode #add character to input
                if PASSWORD_ACTIVE == True: #if password input selected
                    if event.key == p.K_RETURN: #if return key pressed
                        pass
                    elif event.key == p.K_BACKSPACE: #if backspace key pressed
                        PASSWORD_INPUT = PASSWORD_INPUT[:-1] #delete last character
                    elif len(PASSWORD_INPUT) >= 8: #if max length
                        pass
                    else:
                        PASSWORD_INPUT += event.unicode #add character to input
        
        if response == True: #if user login successful
            mainMenu(USERNAME_INPUT, PASSWORD_INPUT) #send to main menu

        if USERNAME_ACTIVE: #if username input selected
            USERNAME_COLOUR = HOVERING_COLOUR #change colour to hovering colour
        else: #if username input deselected
            USERNAME_COLOUR = BASE_COLOUR #change colour to base colour
        
        if PASSWORD_ACTIVE: #if password input selected
            PASSWORD_COLOUR = HOVERING_COLOUR #change colour to hovering colour
        else: #if password input deselected
            PASSWORD_COLOUR = BASE_COLOUR #change colour to base colour

        p.draw.rect(screen, USERNAME_COLOUR, USERNAME_INPUT_RECT, 2) #draw username input rect to screen
        p.draw.rect(screen, PASSWORD_COLOUR, PASSWORD_INPUT_RECT, 2) #draw password input rect to screen

        #draw username input to screen
        USERNAME_SURFACE = p.font.SysFont(SYSTEM_FONT, 75).render(USERNAME_INPUT, True, BASE_COLOUR)
        screen.blit(USERNAME_SURFACE, (USERNAME_INPUT_RECT.x+5, USERNAME_INPUT_RECT.y+15))

        #draw password input to screen        
        PASSWORD_SURFACE = p.font.SysFont(SYSTEM_FONT, 75).render(PASSWORD_INPUT, True, BASE_COLOUR)
        screen.blit(PASSWORD_SURFACE, (PASSWORD_INPUT_RECT.x+5, PASSWORD_INPUT_RECT.y+15))

        p.display.update()

#sign up function
def signUp():
    signup = True #while loop flag variable
    response = False #response flag variable

    screen.fill("White") #turn screen white

    #initialise username input
    USERNAME_INPUT = ""
    USERNAME_INPUT_RECT = p.Rect(350, 160, 395, 75)
    USERNAME_COLOUR = BASE_COLOUR
    USERNAME_ACTIVE = False

    #initialise password input
    PASSWORD_INPUT = ""
    PASSWORD_INPUT_RECT = p.Rect(350, 260, 395, 75)
    PASSWORD_COLOUR = BASE_COLOUR
    PASSWORD_ACTIVE = False

    #initialise confirm password input
    CONFIRM_PASSWORD_INPUT = ""
    CONFIRM_PASSWORD_INPUT_RECT = p.Rect(350, 360, 395, 75)
    CONFIRM_PASSWORD_COLOUR = BASE_COLOUR
    CONFIRM_PASSWORD_ACTIVE = False

    while signup:
        screen.fill("White") #turn screen white
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect
        
        USERNAME_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("USERNAME", True, USERNAME_COLOUR) #username text
        USERNAME_RECT = USERNAME_TEXT.get_rect(center=(175, 200)) #username rect
        
        PASSWORD_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("PASSWORD", True, PASSWORD_COLOUR) #password text
        PASSWORD_RECT = PASSWORD_TEXT.get_rect(center=(175, 300)) #password rect

        CONFIRM_PASSWORD_TEXT = p.font.SysFont(SYSTEM_FONT, 45).render("CONFIRM PASSWORD", True, CONFIRM_PASSWORD_COLOUR) #confirm password text
        CONFIRM_PASSWORD_RECT = PASSWORD_TEXT.get_rect(center=(155, 410)) #confirm password rect

        ENTER_BUTTON = Button(None, pos=(375, 480), text_input="SIGN UP", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #enter button

        screen.blit(MENU_TEXT, MENU_RECT) #draw title text to screen
        screen.blit(USERNAME_TEXT, USERNAME_RECT) #draw username text to screen
        screen.blit(PASSWORD_TEXT, PASSWORD_RECT) #draw password text to screen
        screen.blit(CONFIRM_PASSWORD_TEXT, CONFIRM_PASSWORD_RECT) #draw confirm password text to screen

        for button in [ENTER_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if ENTER_BUTTON.checkForInput(MENU_MOUSE_POS): #on enter button
                    response = asyncio.run(sign_user_up(USERNAME_INPUT, PASSWORD_INPUT, CONFIRM_PASSWORD_INPUT)) #generate response
                if USERNAME_INPUT_RECT.collidepoint(event.pos): #on username input
                    USERNAME_ACTIVE = True #select username input
                else:
                    USERNAME_ACTIVE = False #deselect username input
                if PASSWORD_INPUT_RECT.collidepoint(event.pos): #on password input
                    PASSWORD_ACTIVE = True #select password input
                else:
                    PASSWORD_ACTIVE = False #deselect password input
                if CONFIRM_PASSWORD_INPUT_RECT.collidepoint(event.pos): #on confirm password input
                    CONFIRM_PASSWORD_ACTIVE = True #select confirm password input
                else:
                    CONFIRM_PASSWORD_ACTIVE = False #deselect confirm password input
            if event.type == p.KEYDOWN: #if keyboard button press
                if USERNAME_ACTIVE == True: #if username input selected
                    if event.key == p.K_RETURN: #if return key pressed
                        pass
                    elif event.key == p.K_BACKSPACE: #if backspace key pressed
                        USERNAME_INPUT = USERNAME_INPUT[:-1] #delete last character
                    elif len(USERNAME_INPUT) >= 8: #if max length
                        pass
                    else: #otherwise
                        USERNAME_INPUT += event.unicode #add character to input
                if PASSWORD_ACTIVE == True: #if password input selected
                    if event.key == p.K_RETURN: #if return key pressed
                        pass
                    elif event.key == p.K_BACKSPACE: #if backspace key pressed
                        PASSWORD_INPUT = PASSWORD_INPUT[:-1] #delete last character
                    elif len(PASSWORD_INPUT) >= 8: #if max length
                        pass
                    else: #otherwise
                        PASSWORD_INPUT += event.unicode #add character to input
                if CONFIRM_PASSWORD_ACTIVE == True: #if confirm password input selected
                    if event.key == p.K_RETURN: #if return key pressed
                        pass
                    elif event.key == p.K_BACKSPACE: #if backspace key pressed
                        CONFIRM_PASSWORD_INPUT = CONFIRM_PASSWORD_INPUT[:-1] #delete last character
                    elif len(CONFIRM_PASSWORD_INPUT) >= 8: #if max length
                        pass
                    else: #otherwise
                        CONFIRM_PASSWORD_INPUT += event.unicode #add character to input
        
        if response == True: #if user sign up successful
            logIn() #send to log in

        if USERNAME_ACTIVE: #if username input selected
            USERNAME_COLOUR = HOVERING_COLOUR #change colour to hovering colour
        else: #if username input deselected
            USERNAME_COLOUR = BASE_COLOUR #change colour to base colour
        
        if PASSWORD_ACTIVE: #if password input selected
            PASSWORD_COLOUR = HOVERING_COLOUR #change colour to hovering colour
        else: #if password input deselected
            PASSWORD_COLOUR = BASE_COLOUR #change colour to base colour

        if CONFIRM_PASSWORD_ACTIVE: #if confirm password input selected
            CONFIRM_PASSWORD_COLOUR = HOVERING_COLOUR #change colour to hovering colour
        else: #if confirm password input deselected
            CONFIRM_PASSWORD_COLOUR = BASE_COLOUR #change colour to base colour

        p.draw.rect(screen, USERNAME_COLOUR, USERNAME_INPUT_RECT, 2) #draw username input rect to screen
        p.draw.rect(screen, PASSWORD_COLOUR, PASSWORD_INPUT_RECT, 2) #draw password input rect to screen
        p.draw.rect(screen, CONFIRM_PASSWORD_COLOUR, CONFIRM_PASSWORD_INPUT_RECT, 2) #draw confirm password input rect to screen

        #draw username input to screen
        USERNAME_SURFACE = p.font.SysFont(SYSTEM_FONT, 75).render(USERNAME_INPUT, True, BASE_COLOUR)
        screen.blit(USERNAME_SURFACE, (USERNAME_INPUT_RECT.x+5, USERNAME_INPUT_RECT.y+15))
        
        #draw password input to screen
        PASSWORD_SURFACE = p.font.SysFont(SYSTEM_FONT, 75).render(PASSWORD_INPUT, True, BASE_COLOUR)
        screen.blit(PASSWORD_SURFACE, (PASSWORD_INPUT_RECT.x+5, PASSWORD_INPUT_RECT.y+15))

        #draw confirm password input to screen
        CONFIRM_PASSWORD_SURFACE = p.font.SysFont(SYSTEM_FONT, 75).render(CONFIRM_PASSWORD_INPUT, True, BASE_COLOUR)
        screen.blit(CONFIRM_PASSWORD_SURFACE, (CONFIRM_PASSWORD_INPUT_RECT.x+5, CONFIRM_PASSWORD_INPUT_RECT.y+15))

        p.display.update()

#main menu function
def mainMenu(username, password):
    mainMenu = True #while loop flag variable
    screen.fill("White") #turn screen white
    
    while mainMenu:
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect

        PLAY_BUTTON = Button(None, pos=(375, 250), text_input="PLAY", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #play button
        STATISTICS_BUTTON = Button(None, pos=(375, 350), text_input="STATS", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #stats button

        screen.blit(MENU_TEXT, MENU_RECT) #draw text to screen

        for button in [PLAY_BUTTON, STATISTICS_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS): #on play button
                    difficultyMenu(username, password) #send to difficulty menu
                if STATISTICS_BUTTON.checkForInput(MENU_MOUSE_POS): #on stats button
                    statisticsMenu(username, password) #send to statistics menu
        
        p.display.update()

#difficulty menu function
def difficultyMenu(username, password):
    difficultyMenu = True #while loop flag variable
    screen.fill("White") #turn screen white

    while difficultyMenu:
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect

        EASY_BUTTON = Button(None, pos=(375, 200), text_input="EASY", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #easy button
        MEDIUM_BUTTON = Button(None, pos=(375, 275), text_input="MEDIUM", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #medium button
        HARD_BUTTON = Button(None, pos=(375, 350), text_input="HARD", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #hard button
        LOCAL_BUTTON = Button(None, pos=(375, 425), text_input="LOCAL PvP", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #local button

        screen.blit(MENU_TEXT, MENU_RECT) #draw text to screen

        for button in [EASY_BUTTON, MEDIUM_BUTTON, HARD_BUTTON, LOCAL_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if EASY_BUTTON.checkForInput(MENU_MOUSE_POS): #on easy button
                    main(setSettings(username, password, "easy")) #set easy settings
                if MEDIUM_BUTTON.checkForInput(MENU_MOUSE_POS): #on medium button
                    main(setSettings(username, password, "medium")) #set medium settings
                if HARD_BUTTON.checkForInput(MENU_MOUSE_POS): #on hard button
                    main(setSettings(username, password, "hard")) #set hard settings
                if LOCAL_BUTTON.checkForInput(MENU_MOUSE_POS): #on local button
                    main(setSettings(username, password, "local")) #set local settings
        
        p.display.update()

#statistics menu function
def statisticsMenu(username, password):
    statisticsMenu = True #while loop flag variable
    screen.fill("White") #turn screen white
    
    #grab user's data from database
    conn = sqlite3.connect("userdata.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))
    userData = cur.fetchall()
    conn.close()

    userWins = userData[0][3] #store user's wins
    userDraws = userData[0][4] #store user's draws
    userLosses = userData[0][5] #store user's losses

    while statisticsMenu:
        MENU_MOUSE_POS = p.mouse.get_pos() #grab mouse position

        MENU_TEXT = p.font.SysFont(SYSTEM_FONT, 100).render("CHESS ENGINE", True, BASE_COLOUR) #title text
        MENU_RECT = MENU_TEXT.get_rect(center=(375, 100)) #title rect

        WINS_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("WINS: " + str(userWins), True, BASE_COLOUR) #wins text
        WINS_RECT = WINS_TEXT.get_rect(center=(375, 200)) #wins rect

        DRAWS_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("DRAWS: " + str(userDraws), True, BASE_COLOUR) #draws text
        DRAWS_RECT = DRAWS_TEXT.get_rect(center=(375, 275)) #draws rect

        LOSSES_TEXT = p.font.SysFont(SYSTEM_FONT, 75).render("LOSSES: " + str(userLosses), True, BASE_COLOUR) #losses text
        LOSSES_RECT = LOSSES_TEXT.get_rect(center=(375, 350)) #losses rect

        BACK_BUTTON = Button(None, pos=(375, 425), text_input="BACK", font=p.font.SysFont(SYSTEM_FONT, 75), base_colour=BASE_COLOUR, hovering_colour=HOVERING_COLOUR) #back button

        screen.blit(MENU_TEXT, MENU_RECT) #draw title text to screen
        screen.blit(WINS_TEXT, WINS_RECT) #draw wins text to screen
        screen.blit(DRAWS_TEXT, DRAWS_RECT) #draw draws text to screen
        screen.blit(LOSSES_TEXT, LOSSES_RECT) #draw losses text to screen

        for button in [BACK_BUTTON]:
            button.changeColour(MENU_MOUSE_POS) #change colour if mouse is hovering
            button.update(screen) #draw button to screen
        
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN: #if left click
                if BACK_BUTTON.checkForInput(MENU_MOUSE_POS): #on back button
                    mainMenu(username, password) #send to main menu
        
        p.display.update()

#set settings function
def setSettings(username, password, difficulty):
    if difficulty == "easy":
        return username, password, False, "easy"
    elif difficulty == "medium":
        return username, password, False, "medium"
    elif difficulty == "hard":
        return username, password, False, "hard"
    elif difficulty == "local":
        return username, password, True, "local"

#client logs the user in
async def log_user_in(username, password):
    try:
        reader, writer = await asyncio.open_connection("localhost", 9999)

        #send mode
        writer.write("1".encode())
        await writer.drain()
        print("Mode sent")

        #send username and password
        usernameAndPassword = username + ":" + password
        writer.write(usernameAndPassword.encode())
        await writer.drain()
        print("Username and password sent")

        #get response
        response = await reader.read(1024)

        if response.decode() == "Success": #if user log in successful
            print("Success")
            return True
        else: #if user log in unsuccessful
            print("Fail")
            return False
    except Exception as e: #if error
        print(e) #print error to console
        return False

#client signs the user up
async def sign_user_up(username, password, confirmPassword):
    if password == confirmPassword and len(username) != 0 and len(password) != 0: #if username and password valid
        try:
            reader, writer = await asyncio.open_connection("localhost", 9999)

            #send mode
            writer.write("2".encode())
            await writer.drain()
            print("Mode sent")

            #send username and password
            usernameAndPassword = username + ":" + password
            writer.write(usernameAndPassword.encode())
            await writer.drain()
            print("Username and password sent")

            #get response
            response = await reader.read(1024)

            if response.decode() == "Success": #if user sign up successful
                print("Success")
                return True
            else: #if user sign up unsuccessful
                print("Fail")
                return False
        except Exception as e: #if error
            print(e) #print error to console
            return False
    else: #if password invalid
        print("Fail")
        return False

if __name__ == "__main__":
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    startMenu()
