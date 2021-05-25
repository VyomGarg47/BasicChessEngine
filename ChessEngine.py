"""
This class is reponsible for storing all the information
about the current state of a chess game. It will also be 
responisble for determining the valid moves at the current
state. It will also keep a move log.
"""

class GameState():
	def __init__(self):
		# Board is 8x8 2d List, and each element of the list has 2 char.
		# The first represent the color of the piece, 'b' or 'w'.
		# Second char represent the type of the piece.
		# We can have K,Q,R,B,N,p.
		# The string "--" represent an empty space with no piece.
		self.board = [
			["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
			["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
			["--", "--", "--", "--", "--", "--", "--", "--"],
			["--", "--", "--", "--", "--", "--", "--", "--"],
			["--", "--", "--", "--", "--", "--", "--", "--"],
			["--", "--", "--", "--", "--", "--", "--", "--"],
			["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
			["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
		]

		self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
							  'B': self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
		self.whitetoMove = True
		self.moveLog = []
		self.whiteKingLocation = (7,4)
		self.blackKingLocation = (0,4)
		self.inCheck = False
		self.pins = []
		self.checks = []
		self.checkMate = False
		self.staleMate = False
		self.enpassantPossible = () #co-ordinates where enpassant is possible
		self.enpassantPossibleLog = [self.enpassantPossible]
		#castling rights
		self.currentCastlingRight = CastleRights(True,True,True,True)
		self.CastleRightsLog = [CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
											 self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]

	
	def makeMove(self, move):
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.board[move.startRow][move.startCol] =  "--"
		
		self.moveLog.append(move) #To display History or undo it later
		self.whitetoMove = not self.whitetoMove #Swap players.
		
		#update the king location
		if move.pieceMoved == 'wK':
			self.whiteKingLocation = (move.endRow,move.endCol)
		elif move.pieceMoved == 'bK':
			self.blackKingLocation = (move.endRow,move.endCol)

		#update enpassantPossible variable
		if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
			self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
		else:
			self.enpassantPossible = ()
		#enpassant move
		if move.isEnpassantMove:
			self.board[move.startRow][move.endCol] = '--' #capture the pawn

		#pawn promotion
		if move.isPawnPromotion:
			self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

		self.enpassantPossibleLog.append(self.enpassantPossible)
		#castle move
		if move.isCastleMove:
			if move.endCol - move.startCol == 2: #king side castle
				self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
				self.board[move.endRow][move.endCol+1] = '--'
			else: #queen side castle
				self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
				self.board[move.endRow][move.endCol-2] = '--'
		#update castling rights - whenever its a rook or a king move
		self.updateCastleRights(move)
		self.CastleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
											 self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))
	'''
	undo the last move made
	'''
	def undoMove(self):
		if len(self.moveLog) != 0: # Make sure that there is a move to undo
			move =  self.moveLog.pop()
			self.board[move.startRow][move.startCol]  = move.pieceMoved
			self.board[move.endRow][move.endCol] = move.pieceCaptured
			self.whitetoMove = not self.whitetoMove # Switch Turns back
			# update kings location
			if move.pieceMoved == 'wK':
				self.whiteKingLocation = (move.startRow,move.startCol)
			elif move.pieceMoved == 'bK':
				self.blackKingLocation = (move.startRow,move.startCol)
			#undo the enpassant move
			if move.isEnpassantMove:
				self.board[move.endRow][move.endCol] = '--' #leave landing square blank
				self.board[move.startRow][move.endCol] = move.pieceCaptured
				
			self.enpassantPossibleLog.pop()
			# self.enpassantPossible = self.enpassantPossibleLog[-1]
			newenpassantRights = self.enpassantPossibleLog[-1]
			self.enpassantPossible = newenpassantRights
			
			#undo the castling rights
			self.CastleRightsLog.pop() # get rid of new castle rights
			newRights = self.CastleRightsLog[-1] # set the current castling rights to the last one
			self.currentCastlingRight = CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)

			#undo the castle move
			if move.isCastleMove:
				if move.endCol - move.startCol == 2: 
					self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
					self.board[move.endRow][move.endCol-1] = '--'
				else:
					self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
					self.board[move.endRow][move.endCol+1] = '--'
			

			self.checkMate = False
			self.staleMate = False


	def updateCastleRights(self,move):
		if move.pieceMoved == 'wK':
			self.currentCastlingRight.wks = False
			self.currentCastlingRight.wqs = False

		elif move.pieceMoved == 'bK':
			self.currentCastlingRight.bks = False
			self.currentCastlingRight.bqs = False

		elif move.pieceMoved == 'wR':
			if move.startRow == 7:
				if move.startCol == 0: #left rook
					self.currentCastlingRight.wqs = False
				elif move.startCol == 7:
					self.currentCastlingRight.wks = False

		elif move.pieceMoved == 'bR':
			if move.startRow == 0:
				if move.startCol == 0: #left rook
					self.currentCastlingRight.bqs = False
				elif move.startCol == 7:
					self.currentCastlingRight.bks = False

		#if a rook is captured
		if move.pieceCaptured == 'wR':
			if move.endRow == 7:
				if move.endCol == 0:
					self.currentCastlingRight.wqs = False
				elif move.endCol == 7:
					self.currentCastlingRight.wks = False
		
		elif move.pieceCaptured == 'bR':
			if move.endRow == 0:
				if move.endCol == 0:
					self.currentCastlingRight.bqs = False
				elif move.endCol == 7:
					self.currentCastlingRight.bks = False

	'''
	All Moves considering checks
	'''
	def getValidMoves(self):
		moves = []
		
		self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
		if self.whitetoMove:
			kingRow = self.whiteKingLocation[0]
			kingCol = self.whiteKingLocation[1]
		else:
			kingRow = self.blackKingLocation[0]
			kingCol = self.blackKingLocation[1]
		if self.inCheck:
			if len(self.checks) == 1: #only 1 check, block check or move king
				moves = self.getAllPossibleMoves()
				#to block a check you must move a piece into one of the squares btw the enemy piece and the king
				check = self.checks[0] # check information
				checkRow = check[0]
				checkCol = check[1]
				pieceChecking = self.board[checkRow][checkCol] # enemy piece causing the check
				validSquares = [] #squares that piece a can move to, to prevent check
				#if knight, must capture knight or move king,
				if pieceChecking == 'N':
					validSquares = [(checkRow,checkCol)] #only this square possible, must capture the knight
				else:
					for i in range(1,8):
						validSquare = (kingRow + check[2] * i, kingCol + check[3]*i) #going in the direction of check
						validSquares.append(validSquare) #either move a piece in btw or capture the piece
						if validSquare[0]  == checkRow and validSquare[1] == checkCol: #once you get to the piece, end checks
							break

				for i in range(len(moves)-1,-1,-1): #go through backwards when you are removing from list as iterating
					if moves[i].pieceMoved[1] != 'K': #blocks or capture
						if not (moves[i].endRow,moves[i].endCol) in validSquares:
							if moves[i].isEnpassantMove:
								capturedcol = moves[i].endCol
								capturedrow = moves[i].endRow+1 if self.whitetoMove else moves[i].endRow-1
								if not (capturedrow,capturedcol) in validSquares:
									moves.remove(moves[i])
							else:
								moves.remove(moves[i]) 
			else: #double check
				self.getKingMoves(kingRow,kingCol,moves)
		else: #not in check, so all moves are fine
			moves = self.getAllPossibleMoves()

		if len(moves) == 0:
			if self.inCheck:
				self.checkMate = True
			else:
				self.staleMate = True
		else:
			self.checkMate = False
			self.staleMate = False
		
		return moves # Not gonna worry about chccks/pins right now
	
	
	'''
	All Moves without considering checks
	'''
	def getAllPossibleMoves(self):
		moves = []
		for r in range(len(self.board)): # Number of rows
			for c in range(len(self.board[r])): # Number of columns in giving row
				turn = self.board[r][c][0]
				if (turn == 'w' and self.whitetoMove) or (turn == 'b' and not self.whitetoMove):
					piece = self.board[r][c][1]
					self.moveFunctions[piece](r,c,moves) # call the appropriate move function based on the piece type
		return moves

	'''
	Get all the pawn moves for the pawn located at row, col and add moves to list
	'''
	def getPawnMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1,-1,-1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2],self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		if self.whitetoMove:
			moveAmount  = -1
			startRow = 6
			enemyColor = 'b'
			kingRow,kingCol = self.whiteKingLocation
		else:
			moveAmount= 1
			startRow = 1
			enemyColor = 'w'
			kingRow,kingCol = self.blackKingLocation

		if self.board[r+moveAmount][c] == "--": # 1 square move
			if not piecePinned or pinDirection == (moveAmount,0):
				moves.append(Move((r,c),(r+moveAmount,c),self.board))
				if r==startRow and self.board[r+2*moveAmount][c] == "--":
					moves.append(Move((r,c),(r+2*moveAmount,c),self.board))
		# captures
		if c-1 >=0 : # capture to the left
			if not piecePinned or pinDirection == (moveAmount,-1):
				if self.board[r+moveAmount][c-1][0] == enemyColor:
					moves.append(Move((r,c),(r+moveAmount,c-1),self.board))
				if (r+moveAmount,c-1) == self.enpassantPossible:
					attackingPiece = blockingPiece = False
					if kingRow == r:
						if kingCol < c: #king is left of the pawn
							# inside btw king and pawn: outside range btw pawn order
							insideRange = range(kingCol+1,c-1)
							outsideRange = range(c+1,8)
						else: # king is right of the pawn
							insideRange = range(kingCol-1,c,-1)
							outsideRange = range(c-2,-1,-1)

						for i in insideRange:
							if self.board[r][i] != "--": #some other piece, beside the en-passant pawn, blocks
								blockingPiece = True
						for i in outsideRange:
							square = self.board[r][i]
							if square[0] == enemyColor and (square[1]=='R' or square[1] == 'Q'):
								attackingPiece = True
							elif square != "--":
								blockingPiece = True
					
					if not attackingPiece or blockingPiece:
						moves.append(Move((r,c),(r+moveAmount,c-1),self.board,isEnpassantMove=True))

		if c+1 <= 7:
			if not piecePinned or pinDirection == (moveAmount,1):
				if self.board[r+moveAmount][c+1][0] == enemyColor:
					moves.append(Move((r,c),(r+moveAmount,c+1),self.board))
				if (r+moveAmount,c+1) == self.enpassantPossible:
					attackingPiece = blockingPiece = False
					if kingRow == r:
						if kingCol < c: #king is left of the pawn
							# inside btw king and pawn: outside range btw pawn order
							insideRange = range(kingCol+1,c)
							outsideRange = range(c+2,8)
						else: # king is right of the pawn
							insideRange = range(kingCol-1,c+1,-1)
							outsideRange = range(c-1,-1,-1)

						for i in insideRange:
							if self.board[r][i] != "--": #some other piece, beside the en-passant pawn, blocks
								blockingPiece = True
						for i in outsideRange:
							square = self.board[r][i]
							if square[0] == enemyColor and (square[1]=='R' or square[1] == 'Q'):
								attackingPiece = True
							elif square != "--":
								blockingPiece = True
					
					if not attackingPiece or blockingPiece:
						moves.append(Move((r,c),(r+moveAmount,c+1),self.board,isEnpassantMove=True))
		#add pawn promotion later


	# Get Rook Moves
	def getRookMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1,-1,-1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2],self.pins[i][3])
				if self.board[r][c][1] != 'Q':
					self.pins.remove(self.pins[i])
				break

		directions = ((-1,0),(0,-1),(1,0),(0,1)) #up,left,down,right
		enemyColor = "b" if self.whitetoMove else "w"
		for d in directions:
			for i in range(1,8):
				endRow = r + d[0]*i;
				endCol = c + d[1]*i;
				if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
					if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == "--": # empty space, valid
							moves.append(Move((r,c),(endRow,endCol),self.board))
						elif endPiece[0] == enemyColor: # enemy piece
							moves.append(Move((r,c),(endRow,endCol),self.board))
							break
						else: # same color piece
							break
				else: #off board
					break

	# Get Knight Moves
	def getKnightMoves(self, r, c, moves):
		piecePinned = False
		for i in range(len(self.pins)-1,-1,-1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				self.pins.remove(self.pins[i])
				break

		KnightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
		allyColor = "w" if self.whitetoMove else "b"
		for m in KnightMoves:
			endRow = r + m[0]
			endCol = c + m[1]
			if 0 <= endRow < 8 and 0 <=endCol < 8:
				if not piecePinned:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] != allyColor:
						moves.append(Move((r,c),(endRow,endCol),self.board))
		

	def getBishopMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1,-1,-1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2],self.pins[i][3])
				self.pins.remove(self.pins[i])
				break

		directions = ((-1,-1),(-1,1),(1,-1),(1,1))
		enemyColor = "b" if self.whitetoMove else "w"
		for d in directions:
			for i in range(1,8):
				endRow = r + d[0]*i;
				endCol = c + d[1]*i;
				if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
					if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == "--": # empty space, valid
							moves.append(Move((r,c),(endRow,endCol),self.board))
						elif endPiece[0] == enemyColor: # enemy piece
							moves.append(Move((r,c),(endRow,endCol),self.board))
							break
						else: # same color piece
							break
				else: #off board
					break
	
	# Queen Moves
	def getQueenMoves(self, r, c, moves):
		self.getRookMoves(r,c,moves)
		self.getBishopMoves(r,c,moves)

	# King Moves
	def getKingMoves(self, r, c, moves):
		rowMoves = (-1,-1,-1, 0, 0, 1, 1, 1)
		colMoves = (-1, 0, 1,-1, 1,-1, 0, 1)
		allyColor = "w" if self.whitetoMove else "b"
		for i in range(8):
			endRow = r + rowMoves[i]
			endCol = c + colMoves[i]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor:
					# place king on end square and check for checks
					if allyColor == 'w':
						self.whiteKingLocation = (endRow,endCol)
					else:
						self.blackKingLocation = (endRow,endCol)
					inCheck, pins, checks = self.checkForPinsAndChecks()
					if not inCheck:
						moves.append(Move((r,c),(endRow,endCol),self.board))
					# place king back on original location
					if allyColor == 'w':
						self.whiteKingLocation = (r,c)
					else:
						self.blackKingLocation = (r,c)

		self.getCastleMoves(r,c,moves,allyColor)

	def squareUnderAttack(self,r,c,allyColor): 
		startRow = r
		startCol = c
		enemyColor = 'w' if allyColor == 'b' else 'b'
		directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
		for j in range(len(directions)):
			d = directions[j]
			possiblePin = () # Reset possible pins
			for i in range(1,8):
				endRow = startRow + d[0]*i
				endCol = startCol + d[1]*i
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor: #no attack from that direction
						break
					elif endPiece[0] == enemyColor:
						type = endPiece[1]
						#5 possibilities here
						#1. Orthogonally away from king and piece is a rook
						#2. Diagonally away and piece is a bishop
						#3. 1 sqaure away and pawn
						#4. Any direction and piece is a queen
						#5. Any direction 1 square away and piece is a king
						if (0 <= j <= 3 and type == 'R') or \
							(4 <= j <= 7 and type == 'B') or \
							(i == 1 and type == 'p' and ((enemyColor == 'w' and 6<=j<=7) or (enemyColor=='b' and 4 <= j <= 5))) or \
							(type == 'Q') or (i==1 and type == 'K'):
							return True
						else: #enemy piece is not applying check
							break
				else:
					break
		#check for knight moves
		KnightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
		for m in KnightMoves:
			endRow = startRow + m[0]
			endCol = startCol + m[1]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'N':
					return True

		return False


	def getCastleMoves(self,r,c,moves,allyColor):
		# print(self.currentCastlingRight.wks,self.currentCastlingRight.wqs,self.currentCastlingRight.bks,self.currentCastlingRight.bqs,)
		if self.squareUnderAttack(r,c,allyColor):
			return #can't castle
		if (self.whitetoMove and self.currentCastlingRight.wks) or (not self.whitetoMove and self.currentCastlingRight.bks):
			self.getKingsideCastleMoves(r,c,moves,allyColor)

		if (self.whitetoMove and self.currentCastlingRight.wqs) or (not self.whitetoMove and self.currentCastlingRight.bqs):
			self.getQueensideCastleMoves(r,c,moves,allyColor)			

	def getKingsideCastleMoves(self,r,c,moves,allyColor):
		if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
			if not self.squareUnderAttack(r,c+1,allyColor) and not self.squareUnderAttack(r,c+2,allyColor):
				# print("appending king side castle")
				moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))


	def getQueensideCastleMoves(self,r,c,moves,allyColor):
		if self.board[r][c-1] == '--' and self.board[r][c-2]=='--' and self.board[r][c-3]=='--':
			if not self.squareUnderAttack(r,c-1,allyColor) and not self.squareUnderAttack(r,c-2,allyColor):
				# print("appending queen side castle")
				moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))			


	def checkForPinsAndChecks(self):
		pins = [] # square where the allied pinned piece is and direction pinned from
		checks = [] # square where the enemy is applying a check
		inCheck = False
		if self.whitetoMove:
			enemyColor = "b"
			allyColor = "w"
			startRow = self.whiteKingLocation[0]
			startCol = self.whiteKingLocation[1]
		else:
			enemyColor = "w"
			allyColor = "b"
			startRow = self.blackKingLocation[0]
			startCol = self.blackKingLocation[1]

		# check outward from king for pins and checks, keep track of pins
		directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
		for j in range(len(directions)):
			d = directions[j]
			possiblePin = () # Reset possible pins
			for i in range(1,8):
				endRow = startRow + d[0]*i
				endCol = startCol + d[1]*i
				if 0 <= endRow < 8 and 0 <= endCol < 8:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor and endPiece[1]!='K':
						if possiblePin == ():
							possiblePin = (endRow,endCol,d[0],d[1])
						else: # else, second allied piece, so no pin or check possible in this direction
							break
					elif endPiece[0] == enemyColor:
						type = endPiece[1]
						#5 possibilities here
						#1. Orthogonally away from king and piece is a rook
						#2. Diagonally away and piece is a bishop
						#3. 1 sqaure away and pawn
						#4. Any direction and piece is a queen
						#5. Any direction 1 square away and piece is a king
						if (0 <= j <= 3 and type == 'R') or \
							(4 <= j <= 7 and type == 'B') or \
							(i == 1 and type == 'p' and ((enemyColor == 'w' and 6<=j<=7) or (enemyColor=='b' and 4 <= j <= 5))) or \
							(type == 'Q') or (i==1 and type == 'K'):
							if possiblePin == (): #no piece blocking, so check
								inCheck = True
								checks.append((endRow,endCol,d[0],d[1]))
								break
							else: #piece is blocking the pin
								pins.append(possiblePin)
								break
						else: #enemy piece is not applying check
							break
				else:
					break
		#check for knight moves
		KnightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
		for m in KnightMoves:
			endRow = startRow + m[0]
			endCol = startCol + m[1]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'N':
					inCheck = True
					checks.append((endRow,endCol,m[0],m[1]))

		return inCheck, pins, checks


class CastleRights():
	def __init__(self,wks,bks,wqs,bqs):
		self.wks = wks
		self.bks = bks
		self.wqs = wqs
		self.bqs = bqs


class Move():
	# maps keys to values
	ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
				   "5": 3, "6": 2, "7": 1, "8": 0}
	rowsToRanks = {v: k for k, v in ranksToRows.items()}
	filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
				   "e": 4, "f": 5, "g": 6, "h": 7}
	colsToFiles = {v: k for k, v in filesToCols.items()}
	
	def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
		self.startRow = startSq[0]
		self.startCol = startSq[1]
		self.endRow = endSq[0]
		self.endCol = endSq[1]
		self.pieceMoved = board[self.startRow][self.startCol]
		self.pieceCaptured = board[self.endRow][self.endCol]
		#queen promotion
		self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

		#En passant
		self.isEnpassantMove = isEnpassantMove
		if self.isEnpassantMove:
			self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
		
		self.isCastleMove = isCastleMove
		self.isCapture = self.pieceCaptured != '--'
		self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow*10 + self.endCol
	'''
	Overriding the equals method
	'''
	def __eq__(self,other):
		if isinstance(other,Move):
			return self.moveID == other.moveID
		return False;

	def getChessNotation(self):
		# Future plan -> convert it to real chess notation
		return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)


	def getRankFile(self, r, c):
		return self.colsToFiles[c] + self.rowsToRanks[r];
