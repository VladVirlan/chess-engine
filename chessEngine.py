"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.
It will also keep a move log.
"""

class gameState():
    def __init__(self):
        """
        board is an 8x8 2D array.
        Each element of the array contains 2 characters.
        The first character represents the colour of the piece (either "b" or "w").
        The second character represents what type of piece it is (either "K", "Q", "R", "B", "N" or "P").
        "--" represents an empty space on the board with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves, "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves} #dictionary of all our move functions
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = () #coordinates for the square where an En Passant capture is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    """
    takes a move object as a parameter and executes it (will not work for castling, pawn promotion or en-passant)
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move for later
        self.whiteToMove = not self.whiteToMove #switch turns
        #update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #pawn promotion
        if move.isPawnPromotion: #is this move a pawn promotion?
            """
            askForPiece = True #flag variable for input
            while askForPiece: #ask for piece until valid piece is inputted
                newPiece = input("Promote to a Queen(Q), Rook(R), Bishop(B) or Knight(N): ") #ask for piece in console
                if newPiece == "Q" or newPiece == "R" or newPiece == "B" or newPiece == "N": #if valid piece input
                    askForPiece = False #get out of loop
            """
            newPiece = "Q"
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + newPiece #promote pawn to new piece
        #en passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn
        #update enPassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol) #coordinates of en passant square
        else: #whenever any other move is made
            self.enPassantPossible = () #reset variable
        #update en passant log
        self.enPassantPossibleLog.append(self.enPassantPossible)
        #castle move
        if move.isCastleMove:
            if (move.endCol - move.startCol) == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #moves rook
                self.board[move.endRow][move.endCol+1] = "--" #erase old rook
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #moves rook
                self.board[move.endRow][move.endCol-2] = "--" #erase old rook
        #update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move) #update our castle rights
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)) #add to our castleRightsLog

    """
    undo the last move made
    """
    def undoMove(self):
        if len(self.moveLog) != 0: #make sure that there is a move to undo
            move = self.moveLog.pop() #take the last move out of the moveLog
            self.board[move.startRow][move.startCol] = move.pieceMoved #puts the moved piece where it originally was
            self.board[move.endRow][move.endCol] = move.pieceCaptured #puts the captured piece back
            self.whiteToMove = not self.whiteToMove #switch turns
            #update the king's location if moved
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo en passant move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--" #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured #put piece back where it was
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            #undo castling rights
            self.castleRightsLog.pop() #get rid of the last castling rights
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) #set the current castling rights to the now last one
            #undo castle move
            if move.isCastleMove:
                if (move.endCol - move.startCol) == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] #moves rook back
                    self.board[move.endRow][move.endCol-1] = "--"
                else: #queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] #moves rook back
                    self.board[move.endRow][move.endCol+1] = "--"
            
            self.checkmate = False #when we undo a move we can't be in checkmate
            self.stalemate = False #when we undo a move we can't be in stalemate

    """
    Updates the castle rights given the move
    """
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK": #white king
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK": #black king
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR": #white rooks
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR": #black rooks
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                if move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False

        #if a rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False #white queenside
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False #white kingside
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False #black queenside
                if move.endCol == 7:
                    self.currentCastlingRights.bks = False #black kingside

    """
    generates all moves considering checks
    """
    def getValidMoves(self):
        """
        #naive algorithm
        moves = self.getAllPossibleMoves() #generate all possible moves
        
        for i in range(len(moves)-1, -1, -1): #iterating through list backwards
            self.makeMove(moves[i]) #for each move, make the move - switches turns
            self.whiteToMove = not self.whiteToMove #switch turns back
            if self.inCheck():
                moves.remove(moves[i]) #if it is not a valid move, remove the move from the list of moves
            
            self.undoMove() #undo the made move - switches turns
            self.whiteToMove = not self.whiteToMove #switch turns back

        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                self.checkmate = True #if there are no valid moves left and the king is in check, checkmate
                print("Checkmate!")
            else:
                self.stalemate = True #if there are no valid moves left and the king is not in check, stalemate
                print("Stalemate!")
        else: #makes sure these remain as false until a checkmate or stalemate has actually been made
            self.checkmate = False
            self.stalemate = False

        return moves
        """

        #advanced algorithm
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove: #white's turn
            kingRow = self.whiteKingLocation[0] #find the king's row
            kingCol = self.whiteKingLocation[1] #find the king's column
        else: #black's turn
            kingRow = self.blackKingLocation[0] #find the king's row
            kingCol = self.blackKingLocation[1] #find the king's column
        
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.getAllPossibleMoves() #generate all possible moves
                if self.whiteToMove: #white's turn
                    self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
                else: #black's turn
                    self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
                #to block a check you have to move a piece inbetween the enemy piece and the king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #finds enemy piece causing the check
                validSquares = [] #will hold squares that pieces can move to
                if pieceChecking[1] == "N": #if the enemy piece is a knight, you must capture the knight or move the king
                    validSquares = [(checkRow, checkCol)]
                else: #other pieces can be blocked
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to the checking piece, break 
                            break
                #get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1): #go through the list backwards
                    if moves[i].pieceMoved[1] != "K": #move doesn't move the king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i]) #move must be removed
            else: #double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check, all moves are fine
            moves = self.getAllPossibleMoves()
            if self.whiteToMove: #white's turn
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else: #black's turn
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)          
        if len(moves) == 0: #are there no more valid moves left
            if self.inCheck: #king is in check
                self.checkmate = True #must be checkmate
                #print("Checkmate:", self.checkmate)
            else: #king is not in check
                self.stalemate = True #must be stalemate
                #print("Stalemate:", self.stalemate)
        else: #since there are still valid moves left, it is not checkmate or stalemate
            self.checkmate = False
            self.stalemate = False

        return moves
    
    """
    Returns if the player is in check, a list of pins and a list of checks
    """
    def checkForPinsAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False #initally not in check
        if self.whiteToMove: #white's turn
            enemyColour = "b"
            allyColour = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else: #black's turn
            enemyColour = "w"
            allyColour = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if (0 <= endRow < 8) and (0 <= endCol < 8): #checks square is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColour and endPiece[1] != "K": #checks if piece is allied and if the piece is not a king type piece
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColour: #checks if piece is an enemy
                        type = endPiece[1]
                        """
                        There are 5 possibilities here in this complex conditional statement
                        #1) Orthogonally away from king and piece is a rook
                        #2) Diagonally away from king and piece is a bishop
                        #3) 1 square away diagonally from king and piece is a pawn
                        #4) any direction and piece is a queen
                        #5) any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        """
                        if (0 <= j <= 3) and (type == "R") or \
                            (4 <= j <= 7) and (type == "B") or \
                            ((i == 1 and type == "P") and ((enemyColour == "w" and 6 <= j <= 7) or (enemyColour == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or (i == 1 and type == "K"):
                                if possiblePin == (): #no piece is blocking, so it is a check
                                    inCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                                    break
                                else: #piece is blocking, so it is a pin
                                    pins.append(possiblePin)
                                    break
                        else: #enemy piece is not checking
                            break
                else: #if a piece is off the board
                    break

        #check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColour and endPiece[1] == "N": #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        
        return inCheck, pins, checks
    
    """
    Determines if the current player is in check
    """
    """
    def inCheck(self):
        if self.whiteToMove: #white's turn
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1]) #see if white king is in check
        else: #black's turn
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1]) #see if black king is in check
    """
    
    """
    Determines if the enemy can attack the square (r, c)
    """
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's turn
        oppMoves = self.getAllPossibleMoves() #generate opponent's moves
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves: #iterate through opponent's moves
            if move.endRow == r and move.endCol == c: #square is under attack
                return True #returns that the square is under attack
        return False #returns that the square is not under attack

    """
    generates all moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = [] #empty list
        for r in range(len(self.board)): #loops through rows in board
            for c in range(len(self.board[r])): #loops through cols in given row
                turn = self.board[r][c][0] #stores either b or w
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove): #checks if it is the piece's turn to move
                    piece = self.board[r][c][1] #stores either "K", "Q", "R", "B", "N" or "P"
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function
        
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list of all possible moves
    """
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1): #go through the list of pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c: #if the piece is pinned
                piecePinned = True #sets piece as pinned
                pinDirection = (self.pins[i][2], self.pins[i][3]) #finds what direction the pin is from
                self.pins.remove(self.pins[i]) #removes pin from list
                break

        if self.whiteToMove: #white pawn moves
            kingRow, kingCol = self.whiteKingLocation #find white king

            if self.board[r-1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0): #is it pinned?
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: #captures on the left side of the board
                if not piecePinned or pinDirection == (-1, -1): #is it pinned?
                    if self.board[r-1][c-1][0] == "b": #checks there is an enemy piece to capture
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                    elif (r-1, c-1) == self.enPassantPossible: #EN PASSANT
            
                        attackingPiece = blockingPiece = False #initialise variables
                        if kingRow == r: #if king is on same row
                            if kingCol < c: #if king is on the left
                                insideRange = range(kingCol+1, c-1) #range between king and pawn
                                outsideRange = range(c+1, 8) #range between pawn and border
                            else: #if king is on the right
                                insideRange = range(kingCol-1, c, -1) #range between king and pawn
                                outsideRange = range(c-2, -1, -1) #range between pawn and border
                            
                            for i in insideRange:
                                if self.board[r][i] != "--": #if blocking piece
                                    blockingPiece = True
 
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == "b" and (square[1] == "R" or square[1] == "Q"): #if attacking piece
                                    attackingPiece = True
                                elif square != "--": #if blocking piece
                                    blockingPiece = True
                        
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7: #captures on the right side of the board
                if not piecePinned or pinDirection == (-1, 1): #is it pinned?
                    if self.board[r-1][c+1][0] == "b": #checks there is an enemy piece to capture
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1, c+1) == self.enPassantPossible: #EN PASSANT

                        attackingPiece = blockingPiece = False #initialise variables
                        if kingRow == r: #if king is on same row
                            if kingCol < c: #if king is on the left
                                insideRange = range(kingCol+1, c) #range between king and pawn
                                outsideRange = range(c+2, 8) #range between pawn and border
                            else: #if king is on the right
                                insideRange = range(kingCol-1, c+1, -1) #range between king and pawn
                                outsideRange = range(c-1, -1, -1) #range between pawn and border
                            
                            for i in insideRange:
                                if self.board[r][i] != "--": #if blocking piece
                                    blockingPiece = True
 
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == "b" and (square[1] == "R" or square[1] == "Q"): #if attacking piece
                                    attackingPiece = True
                                elif square != "--": #if blocking piece
                                    blockingPiece = True
                        
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r-1, c+1), self.board, isEnPassantMove=True))

        else: #black pawn moves
            kingRow, kingCol = self.blackKingLocation #find black king
            
            if self.board[r+1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (1, 0): #is it pinned?
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                        moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: #captures on the left side of the board
                if not piecePinned or pinDirection == (1, -1): #is it pinned?
                    if self.board[r+1][c-1][0] == "w": #checks there is an enemy piece to capture
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                    elif (r+1, c-1) == self.enPassantPossible: #EN PASSANT

                        attackingPiece = blockingPiece = False #initialise variables
                        if kingRow == r: #if king is on same row
                            if kingCol < c: #if king is on the left
                                insideRange = range(kingCol+1, c-1) #range between king and pawn
                                outsideRange = range(c+1, 8) #range between pawn and border
                            else: #if king is on the right
                                insideRange = range(kingCol-1, c, -1) #range between king and pawn
                                outsideRange = range(c-2, -1, -1) #range between pawn and border
                            
                            for i in insideRange:
                                if self.board[r][i] != "--": #if blocking piece
                                    blockingPiece = True
 
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == "w" and (square[1] == "R" or square[1] == "Q"): #if attacking piece
                                    attackingPiece = True
                                elif square != "--": #if blocking piece
                                    blockingPiece = True
                        
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r+1, c-1), self.board, isEnPassantMove=True))

            if c+1 <= 7: #captures on the right side of the board
                if not piecePinned or pinDirection == (1, 1): #is it pinned?
                    if self.board[r+1][c+1][0] == "w": #checks there is an enemy piece to capture
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                    elif (r+1, c+1) == self.enPassantPossible: #EN PASSANT

                        attackingPiece = blockingPiece = False #initialise variables
                        if kingRow == r: #if king is on same row
                            if kingCol < c: #if king is on the left
                                insideRange = range(kingCol+1, c) #range between king and pawn
                                outsideRange = range(c+2, 8) #range between pawn and border
                            else: #if king is on the right
                                insideRange = range(kingCol-1, c+1, -1) #range between king and pawn
                                outsideRange = range(c-1, -1, -1) #range between pawn and border
                            
                            for i in insideRange:
                                if self.board[r][i] != "--": #if blocking piece
                                    blockingPiece = True
 
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == "w" and (square[1] == "R" or square[1] == "Q"): #if attacking piece
                                    attackingPiece = True
                                elif square != "--": #if blocking piece
                                    blockingPiece = True
                        
                        if not attackingPiece or blockingPiece:
                            moves.append(Move((r, c), (r+1, c+1), self.board, isEnPassantMove=True))

    """
    Get all the rook moves for the rook located at row, col and add these moves to the list of all possible moves
    """
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1): #look through pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c: #if piece is pinned
                piecePinned = True #sets piece as pinned
                pinDirection = (self.pins[i][2], self.pins[i][3]) #finds what direction the pin is from
                if self.board[r][c][1] != "Q": #can't remove queen from pin on rook moves, only on bishop moves
                    self.pins.remove(self.pins[i]) #remove pin from list
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #what directions the rook can move in
        enemyColour = "b" if self.whiteToMove else "w" #finds out who the opposing colour is
        for d in directions: #looping through all four directions
            for i in range(1, 8):
                endRow = r + d[0] * i #each iteration of i goes up a space on the board in the direction we are checking
                endCol = c + d[1] * i
                if (0 <= endRow < 8) and (0 <= endCol < 8): #checks if the space is on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): #is it pinned?
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #checks if it is an empty space - valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColour: #checks if it is an enemy piece - valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break #makes sure we don't go any further up the board
                        else: #otherwise it must be a friendly piece - invalid
                            break #makes sure we don't go any further up the board
                else: #otherwise must be off the board
                    break #makes sure we don't go off the board

    """
    Get all the knight moves for the knight located at row, col and add these moves to the list of all possible moves
    """
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1): #loop through pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c: #if it is pinned
                piecePinned = True #set piece to pinned
                self.pins.remove(self.pins[i]) #remove pin from list
                break

        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #what directions the knight can move in
        allyColour = "w" if self.whiteToMove else "b" #finds out the allied colour
        for d in directions: #looping through all the knight's possible directions
            endRow = r + d[0] #finds the endRow of this move
            endCol = c + d[1] #finds the endCol of this move
            if (0 <= endRow < 8) and (0 <= endCol < 8): #checks it is on the board
                if not piecePinned: #is it pinned?
                    endPiece = self.board[endRow][endCol] #finds this space on the board
                    if endPiece[0] != allyColour: #if the space is not an allied colour, then it must be empty or an enemy - valid
                        moves.append(Move((r, c), (endRow, endCol), self.board)) #append move

    """
    Get all the bishop moves for the bishop located at row, col and add these moves to the list of all possible moves
    """
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1): #loop through pins backwards
            if self.pins[i][0] == r and self.pins[i][1] == c: #if it is pinned
                piecePinned = True #set piece to pinned
                pinDirection = (self.pins[i][2], self.pins[i][3]) #finds what direction the pin is
                self.pins.remove(self.pins[i]) #remove pin from list
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #what directions the bishop can move in
        enemyColour = "b" if self.whiteToMove else "w" #finds out who the opposing colour is
        for d in directions: #looping through all four directions
            for i in range(1, 8):
                endRow = r + d[0] * i #each iteration of i goes up a space on the board in the direction we are checking
                endCol = c + d[1] * i
                if (0 <= endRow < 8) and (0 <= endCol < 8): #checks if the space is on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): #is it pinned?
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #checks if it is an empty space - valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColour: #checks if it is an enemy piece - valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break #makes sure we don't go any further up the board
                        else: #otherwise it must be a friendly piece - invalid
                            break #makes sure we don't go any further up the board
                else: #otherwise must be off the board
                    break #makes sure we don't go off the board
    
    """
    Get all the queen moves for the queen located at row, col and add these moves to the list of all possible moves
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    """
    Get all the king moves for the king located at row, col and add these moves to the list of all possible moves
    """
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1) #list of row moves for the king
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1) #list of column moves for the king
        allyColour = "w" if self.whiteToMove else "b" #finds allied colour
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if (0 <= endRow < 8) and (0 <= endCol < 8): #is it on the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour: #not an ally piece (empty or enemy piece)
                    #place king on the end square and check for checks
                    if allyColour == "w": #white's turn
                        self.whiteKingLocation = (endRow, endCol)
                    else: #black's turn
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck: #is the king in check?
                        moves.append(Move((r, c), (endRow, endCol), self.board)) #if not, this is a valid move
                    #place king back on original location
                    if allyColour == "w": #white's turn
                        self.whiteKingLocation = (r, c)
                    else: #black's turn
                        self.blackKingLocation = (r, c)

    """
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    """
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves) #white or black can castle king side
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves) #white or black can castle queen side

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        #king side
        self.wks = wks
        self.bks = bks
        #queen side
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0} #maps the ranks in real life chess to the rows on our board
    rowsToRanks = {v: k for k, v in ranksToRows.items()} #flips the keys and values around
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7} #maps the files in real life chess to the columns on our board
    colsToFiles = {v: k for k, v in filesToCols.items()} #flips the keys and values around

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #could also be an empty square
        #pawn promotion        
        self.isPawnPromotion = False #pawn promotion flag variable
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7): #is the piece moved a pawn and is it on the back rank?
            self.isPawnPromotion = True #flag as true
        #en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        #castling
        self.isCastleMove = isCastleMove
        #capture move
        self.isCaptureMove = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #unique ID created for each move 0000-7777

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    """
    Overriding the str() function
    """
    def __str__(self):
        #castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O" #return kingside else queenside
        
        endSquare = self.getRankFile(self.endRow, self.endCol)
        #pawn moves
        if self.pieceMoved[1] == "P":
            if self.isCaptureMove:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare    
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCaptureMove:
            moveString += "x"
        return moveString + endSquare