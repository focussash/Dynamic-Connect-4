import copy
DefaultBoard = [[1,1,1,7,7,7,1,1,1,7,7,7],[2,4,6,1,3,5,3,5,7,2,4,6],1,0]

class Board:
    global DefaultBoard

    def __init__ (Self,InitialState = DefaultBoard):
        #Initiate the board formation; if there is no input then use the default board formation
        Self.State = InitialState
        Self.BoardArrayB = []
        Self.BoardArrayA = []
        Self.BoardGraph = [] #Graphical representation of current state
        Self.Action = ''
        Self.SearchTree = []

    def GenerateBoard(Self):
        #This generates a bit board of the current board (an array of 8*8 binary numbers; the bottom row and rightmost column are all 0s to avoid TerminalTest errors)
        FoundPiece = 0
        for i in range(1,8):
            for j in range(1,8):
                for k in range(12):
                    if Self.State[1][k] == i:
                        if Self.State[0][k] == j:
                            FoundPiece = 1
                            if k < 6:
                                Self.BoardArrayB.append(0)
                                Self.BoardArrayA.append(1)
                            else:
                                Self.BoardArrayB.append(1)
                                Self.BoardArrayA.append(0)
                if FoundPiece == 0:
                   Self.BoardArrayB.append(0)
                   Self.BoardArrayA.append(0)
                FoundPiece = 0
            Self.BoardArrayB.append(0)
            Self.BoardArrayA.append(0)
        for m in range(8):
            Self.BoardArrayB.append(0)
            Self.BoardArrayA.append(0)

    def GenerateGraph(Self):
        print('  1 2 3 4 5 6 7')
        for i in range (7):
            print(str(i+1), end = '')
            print(' ', end = '')
            for j in range (13):
                if j % 2 > 0:
                    print(',', end = '')
                else:
                    if Self.BoardArrayA[i*8+int(j/2)] == 1:
                        print('X', end = '')
                    elif Self.BoardArrayB[i*8+int(j/2)] == 1:
                        print('O', end = '')
                    else:
                        print(' ', end = '')
            print('\n')


    def Update(Self,Action):
        #Apply an action (moving one piece) to update the board

        X = int(Action[0])
        Y = int(Action[1])
        Act = Action[2]
       
        #Now, find the piece to update
        for x in range(12):
            if Self.State[0][x] == X and Self.State[1][x] == Y:
                PieceNumber = x
        #Now, update the corresponding piece
        if Act == 'N':
            Self.State[1][PieceNumber] -= 1
        elif Act == 'S':
            Self.State[1][PieceNumber] += 1
        elif Act == 'E':
            Self.State[0][PieceNumber] += 1
        elif Act == 'W':
            Self.State[0][PieceNumber] -= 1

    def GenerateTotalBoard(Self):
        #Does an bitwise or operation on BoardArrayA and BoardArrayB, but this doesn't seem needed for computation of this problem
        StrA = "".join(map(str, Self.BoardArrayA))
        StrB = "".join(map(str, Self.BoardArrayB))
        BitNumA = int(StrA,base = 2)
        BitNumB = int(StrB,base = 2)
        TotalBoard = BitNumA | BitNumB

    def TerminalTest(Self):
        #Check if the game ended; Also assigns utility: 1 = player A wins, -1 = player B wins
        StrA = "".join(map(str, Self.BoardArrayA))
        StrB = "".join(map(str, Self.BoardArrayB))
        BitNumA = int(StrA,base = 2)
        BitNumB = int(StrB,base = 2)
        #Horizontal
        if BitNumA & BitNumA >> 1 & BitNumA >> 2 & BitNumA >> 3:
            return 1
        if BitNumB & BitNumB >> 1 & BitNumB >> 2 & BitNumB >> 3:
            return -1
        #Vertical
        if BitNumA & BitNumA >> 8 & BitNumA >> 16 & BitNumA >> 24:
            return 1
        if BitNumB & BitNumB >> 8 & BitNumB >> 16 & BitNumB >> 24:
            return -1
        #Two kinds of diagnal (right and left, respectively)
        if BitNumA & BitNumA >> 9 & BitNumA >> 18 & BitNumA >> 27:
            return 1
        if BitNumB & BitNumB >> 9 & BitNumB >> 18 & BitNumB >> 27:
            return -1
        if BitNumA & BitNumA >> 7 & BitNumA >> 14 & BitNumA >> 21:
            return 1
        if BitNumB & BitNumB >> 7 & BitNumB >> 14 & BitNumB >> 21:
            return -1



        
def GenerateChild(State):
    #Generate all child nodes of a given node
    #Start by picking a piece in the board
    #Moves: 1 = E, 2 = W, 3 = S, 4 = N
    ChildTemp = copy.deepcopy(State)
    ChildTemp[2] *= -1 #In the child, it's next player's term
    ChildAll = []
    DuplicateCheck = []
    del_list = [] #Store the list of nodes that overlaps pieces
    if State[2] == 1:
        player = range(6)
    else:
        player = range(6,12)
    for i in player:            
        if ChildTemp[0][i] != 1:
            ChildTemp[0][i] -= 1 #Applying 'W'
            ChildAll.append(ChildTemp)
            ChildTemp = copy.deepcopy(State)
            ChildTemp[2] *= -1
        if ChildTemp[0][i] != 7:
            ChildTemp[0][i] += 1 #Applying 'E'
            ChildAll.append(ChildTemp)
            ChildTemp = copy.deepcopy(State)
            ChildTemp[2] *= -1
        if ChildTemp[1][i] != 1:
            ChildTemp[1][i] -= 1 #Applying 'S'
            ChildAll.append(ChildTemp)
            ChildTemp = copy.deepcopy(State)
            ChildTemp[2] *= -1
        if ChildTemp[1][i] != 7:
            ChildTemp[1][i] += 1 #Applying 'N'
            ChildAll.append(ChildTemp)
            ChildTemp = copy.deepcopy(State)
            ChildTemp[2] *= -1
    #Now, check if the move causes 2 pieces to overlap
    for j in range(len(ChildAll)):
        for k in range(12):
            DuplicateCheck.append([ChildAll[j][0][k],ChildAll[j][1][k]])                
        if len(DuplicateCheck) != len(set(map(tuple,DuplicateCheck))):
            del_list.append(ChildAll[j])
        DuplicateCheck.clear()
    for p in range(len(del_list)):
        ChildAll.remove(del_list[p])
    return ChildAll


currentBoard = [[1,2,3,2,7,7,3,2,6,4,7,1],[1,2,3,4,3,4,4,5,5,3,5,6],1,0]       
a = Board(currentBoard)
b = GenerateChild(a.State)
c = GenerateChild(b[0])
d = GenerateChild(c[0])
for i in range(len(d)):
    print(d[i])