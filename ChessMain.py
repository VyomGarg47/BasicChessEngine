# This is our main driver file.
# Responsible for handling user input and displaying the
# Current Game state

import pygame as p
import ChessEngine,SmartMoveFinder

BOARD_WIDTH = BOARD_HEIGHT = 512 #Could choose 400 also
MOVE_LOG_PANEL_WIDTH = 280
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENTION = 8 #Dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENTION
MAX_FPS = 15 #for animations
IMAGES = {}

'''
Initialize a global dictionary of images.
This will be called exactly once in the main
'''

def loadImages():
	pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
	for piece in pieces:
		IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))
	#Note: we can access an image by saying 'IMAGES['wp']'


#This is the main driver, handling the user input and updating the graphics

def main():
	p.init()
	screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
	clock = p.time.Clock()
	screen.fill(p.Color("white"))
	moveLogFont = p.font.SysFont('Arial',18,False,False)
	gs = ChessEngine.GameState()
	validMoves = gs.getValidMoves() #This is a expensive operation
	moveMade = False # Flag Variable
	animate = False
	# As we don't want to generate this every frame
	loadImages() #only do this once
	running = True
	sqSelected = () #no square is selected initially, it will be a tuple: (row,col)
	playerClicks = [] #keep track of player clicks (two tuples:[(6,4),(4,4)])
	gameOver = False
	playerOne = False #if human is playing white, then this will be true, if an AI is playing, then false
	playerTwo = False #same as above but for black
	while running:
		humanTurn = ((gs.whitetoMove and playerOne) or (not gs.whitetoMove and playerTwo))
		for e in p.event.get():
			if e.type == p.QUIT:
				running = False

			# Mouse Handler
			elif e.type == p.MOUSEBUTTONDOWN:
				if not gameOver and humanTurn:
					location =  p.mouse.get_pos() #x,y location of mouse			
					col = location[0]//SQ_SIZE
					row = location[1]//SQ_SIZE

					if sqSelected == (row,col) or col >= 8: #user clicks the same square twice
						sqSelected = () #deselect
						playerClicks = [] #clear player clicks
					else: 
						sqSelected = (row,col)
						playerClicks.append(sqSelected) #if first, then append to first, if second, then append to second
					#was that the user's second click ?
					if len(playerClicks) == 2: #after the second click, we want to make a move
						move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
						print(move.getChessNotation())
						for i in range(len(validMoves)):
							if move == validMoves[i]:
								print("valid move")
								gs.makeMove(validMoves[i])
								moveMade = True
								animate = True
								sqSelected = () #Reset user clicks
								playerClicks = []
						if not moveMade: #Not a valid move, hence reset the click
							playerClicks = [sqSelected]
			# Key Handler
			elif e.type == p.KEYDOWN:
				if e.key == p.K_z: # Undo when 'z' is pressed
					gs.undoMove()
					moveMade = True
					animate = False
					gameOver = False
				
				if e.key == p.K_r: #reset the board when 'r' is pressed
					gs = ChessEngine.GameState()
					validMoves = gs.getValidMoves()
					sqSelected = ()
					playerClicks = []
					moveMade = False
					animate = False
					gameOver = False
		
		#AI move finder logic
		if not gameOver and not humanTurn:
			AImove = SmartMoveFinder.findBestMove(gs,validMoves)
			if AImove is None:
				print("No move found")
				AImove = SmartMoveFinder.findRandomMove(validMoves)
			gs.makeMove(AImove)
			moveMade = True
			animate = True

		if moveMade:
			if len(gs.moveLog) > 0 and animate:
				animateMove(gs.moveLog[-1],screen,gs.board,clock)
			validMoves = gs.getValidMoves()
			moveMade = False
			
		drawGameState(screen,gs,validMoves,sqSelected,moveLogFont)
		
		if gs.checkMate:
			gameOver = True
			if gs.whitetoMove:
				drawEndGameText(screen,"Black wins by checkmate")
			else:
				drawEndGameText(screen,"White wins by checkmate")
		elif gs.staleMate:
			gameOver = True
			drawEndGameText(screen,"Gameover by Stalemate")
		
		clock.tick(MAX_FPS)
		p.display.flip()


#Draws the square. The top left square is always light (from both black and white perspective)
def drawBoard(screen):
	global colors
	colors = [p.Color('white'),p.Color("grey")]
	for r in range(DIMENTION):
		for c in range(DIMENTION):
			color = colors[((r+c)%2)]
			p.draw.rect(screen, color, p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE)) #x,y so c,r


'''
Square selected and moves for piece selected
'''
def highlightSquares(screen,gs,validMoves,sqSelected):
	if sqSelected != ():
		r,c = sqSelected
		if gs.board[r][c][0] == ('w' if gs.whitetoMove else 'b'): #square selected is a piece that can be moved
			#highlight the selected square
			s = p.Surface((SQ_SIZE,SQ_SIZE))
			s.set_alpha(100) #Transperancy ->0 transparent, 255 -> solid
			s.fill(p.Color('blue'))
			screen.blit(s, (c*SQ_SIZE,r*SQ_SIZE))
			#highlight moves from that square
			s.fill(p.Color('yellow'))
			for move in validMoves:
				if move.startRow == r and move.startCol == c:
					screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

'''
Reponsible for all the graphics within a current game state
'''
def drawGameState(screen,gs,validMoves, sqSelected,moveLogFont):
	drawBoard(screen) #Draw squares on the board
	highlightSquares(screen,gs,validMoves,sqSelected)
	drawPieces(screen,gs.board) #Draw pieces on top of those squares
	drawMoveLog(screen,gs,moveLogFont)


'''
Draws move log
'''
def drawMoveLog(screen,gs,font):
	moveLogRect = p.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
	p.draw.rect(screen,p.Color("black"),moveLogRect)
	moveLog = gs.moveLog
	moveTexts = [] #modify this later
	for i in range(0,len(moveLog), 2):
		moveString = str(i//2 + 1) + "." + moveLog[i].getChessNotation() + " "
		if i + 1 < len(moveLog): #adding black move
			moveString += moveLog[i+1].getChessNotation()
		moveTexts.append(moveString)

	movesPerRow = 3
	padding = 5
	textY = padding
	lineSpacing = 2
	for i in range(0,len(moveTexts), movesPerRow):
		text = ""
		for j in range(movesPerRow):
			if i+j < len(moveTexts):
				text += moveTexts[i+j] + " "
		text+= " "
		textObject = font.render(text,True,p.Color('white'))
		textLocation = moveLogRect.move(padding,textY)
		screen.blit(textObject,textLocation)
		textY += textObject.get_height() + lineSpacing
	# textObject = font.render(text,0,p.Color('Black'))
	# screen.blit(textObject,textLocation.move(2,2))

#Draw the pieces on board using the current GameState.board
def drawPieces(screen,board):
	for r in range(DIMENTION):
		for c in range(DIMENTION):
			piece = board[r][c]
			if piece != "--": #Not an empty square
				screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

'''
Animating a move
'''
def animateMove(move,screen,board,clock):
	global colors
	dR = move.endRow - move.startRow
	dC = move.endCol - move.startCol
	framesPerSquare = 5 #frames to move 1 square
	frameCount = (abs(dR) + abs(dC)) * framesPerSquare
	for frame in range(frameCount+1):
		r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
		drawBoard(screen)
		drawPieces(screen,board)
		#erase the piece moved from its ending square
		color = colors[(move.endRow + move.endCol) % 2]
		endSquare = p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
		p.draw.rect(screen,color,endSquare)
		#draw the captured piece onto rectange
		if move.pieceCaptured != '--':
			if move.isEnpassantMove:
				enPassantRow = move.endRow + 1 if move.pieceCaptured[0]=='b' else move.endRow-1
				endSquare = p.Rect(move.endCol*SQ_SIZE,enPassantRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
			screen.blit(IMAGES[move.pieceCaptured],endSquare)
		#draw moving piece
		screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
		p.display.flip()
		clock.tick(60)

def drawEndGameText(screen,text):
	font = p.font.SysFont("Helvitca",40,True,False)
	textObject = font.render(text,0,p.Color('Gray'))
	textLocation = p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
	screen.blit(textObject,textLocation)
	textObject = font.render(text,0,p.Color('Black'))
	screen.blit(textObject,textLocation.move(2,2))

if __name__ == "__main__":
	main()