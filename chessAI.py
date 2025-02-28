"""
This module will deal with any of our AI responsibilities 
"""

import random

pieceScores = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1} #dictionary of our pieces and their respective material values

#positional scores
knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]] 

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "Q": queenScores, "B": bishopScores, "R": rookScores, "bP": blackPawnScores, "wP": whitePawnScores}

CHECKMATE = 1000 #score for finding a checkmate
STALEMATE = 0  #score for finding a stalemate
DEPTH = 3 #depth for recursive functions

"""
Picks and returns a random move
"""
def findRandomMove(validMoves):
    return random.choice(validMoves)

"""
Finds the greediest move based on material alone
"""
def findGreedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1 #returns turn multiplier based on what colour's turn it is
    maxScore = -CHECKMATE #worst possible score
    greedyMove = None #empty best move
    random.shuffle(validMoves) #shuffles valid moves
    
    for playerMove in validMoves: #for every valid move
        gs.makeMove(playerMove) #make the move
        if gs.checkmate:
            score = CHECKMATE #set score if checkmate is found
        elif gs.stalemate:
            score = STALEMATE #set score if stalemate is found
        else:
            score = turnMultiplier * scoreMaterial(gs.board) #score the board
        if score > maxScore: #if score is better
            maxScore = score #new max score
            greedyMove = playerMove #new best move
        gs.undoMove() #undo the move
    
    return greedyMove

"""
Finds the best move on the board - minmax no recursion
"""
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1 #returns turn multiplier based on what colour's turn it is
    opponentMinMaxScore = CHECKMATE #opponents worst possible move
    bestPlayerMove = None #empty best move
    random.shuffle(validMoves) #shuffles valid moves
    
    for playerMove in validMoves: #for every valid move
        gs.makeMove(playerMove) #make the move
        opponentMoves = gs.getValidMoves() #get opponents moves
        #find opponentMaxScore
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves: #look through opponents moves
                gs.makeMove(opponentMove) #make the opponents move
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE #set score if checkmate is found
                elif gs.stalemate:
                    score = STALEMATE #set score if stalemate is found
                else:
                    score = -turnMultiplier * scoreBoard(gs) #score the board
                if score > opponentMaxScore: #if score is better
                    opponentMaxScore = score #new max score
                gs.undoMove() #undo opponent move
        if opponentMaxScore < opponentMinMaxScore: #if max score is less than minmax score 
            opponentMinMaxScore = opponentMaxScore #set new minmax score
            bestPlayerMove = playerMove #set new best move
        gs.undoMove() #undo the move
    return bestPlayerMove

"""
Helper function to make first recursive call
"""
def findBestMoveMinMax(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None #set nextMove to None
    random.shuffle(validMoves) #shuffles valid moves
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove) #call minMax algorithm
    returnQueue.put(nextMove) #add nextMove to the queue

"""
Finds the best move on the board recursively (minmax algorithm)
"""
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0: #terminal node
        return scoreBoard(gs) #score the board
    
    if whiteToMove: #white's turn
        maxScore = -CHECKMATE #set max score
        for move in validMoves: #loop through valid moves
            gs.makeMove(move) #make the move
            nextMoves = gs.getValidMoves() #get the next moves
            score = findMoveMinMax(gs, nextMoves, depth-1, False) #recursive function call
            if score > maxScore: #higher score?
                maxScore = score #set new max score
                if depth == DEPTH: #if depth is equal to max depth
                    nextMove = move #set new next move
            gs.undoMove() #undo the move
        return maxScore #return the max score

    else: #black's turn
        minScore = CHECKMATE #set min score
        for move in validMoves: #loop through valid moves
            gs.makeMove(move) #make the move
            nextMoves = gs.getValidMoves() #get the next moves
            score = findMoveMinMax(gs, nextMoves, depth-1, True) #recursive function call
            if score < minScore: #lower score?
                minScore = score #set new min score
                if depth == DEPTH: #if depth is equal to max depth
                    nextMove = move #set new next move
            gs.undoMove() #undo the move
        return minScore #return the max score

"""
Helper function to make first recursive call with alpha beta pruning
"""
def findBestMoveMinMaxAlphaBeta(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None #set nextMove to None
    random.shuffle(validMoves) #shuffles valid moves
    findMoveMinMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, gs.whiteToMove) #call minMax algorithm
    returnQueue.put(nextMove) #add nextMove to the queue

"""
Finds the best move on the board recursively with alpha beta pruning (minmax algorithm)
"""
def findMoveMinMaxAlphaBeta(gs, validMoves, depth, alpha, beta, whiteToMove):
    global nextMove
    if depth == 0: #terminal node
        return scoreBoard(gs) #score the board

    if whiteToMove: #white's turn
        maxScore = -CHECKMATE #set max score
        for move in validMoves: #loop through valid moves
            gs.makeMove(move) #make the move
            nextMoves = gs.getValidMoves() #get the next moves
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth-1, alpha, beta, False) #recursive function call
            if score > maxScore: #higher score?
                maxScore = score #set new max score
                if depth == DEPTH: #if depth is equal to max depth
                    nextMove = move #set new next move
            gs.undoMove() #undo the move
            if maxScore > beta: #pruning
                break
            if maxScore > alpha:
                alpha = maxScore
        return maxScore #return the max score

    else: #black's turn
        minScore = CHECKMATE #set min score
        for move in validMoves: #loop through valid moves
            gs.makeMove(move) #make the move
            nextMoves = gs.getValidMoves() #get the next moves
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth-1, alpha, beta, True) #recursive function call
            if score < minScore: #lower score?
                minScore = score #set new min score
                if depth == DEPTH: #if depth is equal to max depth
                    nextMove = move #set new next move
            gs.undoMove() #undo the move
            if minScore < alpha: #pruning
                break
            if minScore < beta:
                beta = minScore
        return minScore #return the max score

"""
Helper function to make first recursive call
"""
def findBestMoveNegaMax(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None #set nextMove to None
    random.shuffle(validMoves) #shuffles valid moves
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1) #call negaMax algorithm
    returnQueue.put(nextMove) #add nextMove to the queue

"""
Finds the best move on the board recursively (negamax algorithm)
"""
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0: #terminal node
        return turnMultiplier * scoreBoard(gs) #score the board
    
    maxScore = -CHECKMATE #set max score
    for move in validMoves: #loop through valid moves
        gs.makeMove(move) #make the move
        nextMoves = gs.getValidMoves() #get the next moves
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier) #must be * -1 because we are looking at opponent's moves
        if score > maxScore: #higher score?
            maxScore = score #set new max score
            if depth == DEPTH: #if depth is equal to max depth
                nextMove = move #set new next move
        gs.undoMove() #undo the move
    return maxScore

"""
Helper function to make first recursive call with alpha beta pruning (negamax algorithm)
"""
def findBestMoveNegaMaxAlphaBeta(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None #set nextMove to None
    random.shuffle(validMoves) #shuffles valid moves
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1) #call minMax algorithm
    returnQueue.put(nextMove) #add nextMove to the queue

"""
Finds the best move on the board recursively with alpha beta pruning (negamax algorithm)
"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0: #terminal node
        return turnMultiplier * scoreBoard(gs) #score the board

    maxScore = -CHECKMATE #set max score
    for move in validMoves: #loop through valid moves
        gs.makeMove(move) #make the move
        nextMoves = gs.getValidMoves() #get the next moves
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier) #must be * -1 because we are looking at opponent's moves
        if score > maxScore: #higher score?
            maxScore = score #set new max score
            if depth == DEPTH: #if depth is equal to max depth
                nextMove = move #set new next move
        gs.undoMove() #undo the move
        if maxScore > alpha: #pruning
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

"""
Score the board based on position and material
"""
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--": #if not empty
                #score positionally
                piecePositionScore = 0
                if square[1] != "K": #if not king
                    if square[1] == "P": #if pawn
                        piecePositionScore = piecePositionScores[square][row][col] #returns position score
                    else: #if other piece
                        piecePositionScore = piecePositionScores[square[1]][row][col] #returns position score

                if square[0] == "w": #if piece is white
                    score += pieceScores[square[1]] + piecePositionScore * .1 #add to total score
                elif square[0] == "b": #if piece is black
                    score -= pieceScores[square[1]] + piecePositionScore * .1 #subtract from total score
    
    return score

"""
Score the board based on material
"""
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w": #if piece is white
                score += pieceScores[square[1]] #add to total score
            elif square[0] == "b": #if piece is black
                score -= pieceScores[square[1]] #subtract from total score
    
    return score