import copy
import time
import profile
DefaultBoard = [[1,1,1,7,7,7,1,1,1,7,7,7],[2,4,6,1,3,5,3,5,7,2,4,6],1,0,0]
TotalStatesExplored = 0
class Board:
    global DefaultBoard

    def __init__ (Self,InitialState = DefaultBoard):
        #Initiate the board formation; if there is no input then use the default board formation
        Self.State = InitialState
        Self.Action = ''
        Self.SearchTree = []

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
        
def GenerateBoard(State):
    #This generates a bitboard of the current board (an array of 8*8 binary numbers; the bottom row and rightmost column are all 0s to avoid TerminalTest errors)
    BoardArrayA = [0]*64
    BoardArrayB = [0]*64
    for k in range(6):
        BoardArrayA[State[0][k]+8*State[1][k]] = 1
    for k in range(6,12):
        BoardArrayB[State[0][k]+8*State[1][k]] = 1 
    return BoardArrayA + BoardArrayB

def GenerateGraph(BoardArray):
    #Generate a graphical representation of current board for user
    #Takes input from GenerateBoard
    print('  1 2 3 4 5 6 7')
    for i in range (7):
        print(str(i+1), end = '')
        print(' ', end = '')
        for j in range (13):
            if j % 2 > 0:
                print(',', end = '')
            else:
                if BoardArray[i*8+int(j/2)] == 1:
                    print('X', end = '')
                elif BoardArray[i*8+int(j/2)+64] == 1:
                    print('O', end = '')
                else:
                    print(' ', end = '')
        print('\n')


def TerminalTest(BoardArray):
    #Check if the game ended; Also assigns utility: 1 = player A wins, -1 = player B wins
    #Takes input from GenerateBoard
    StrA = "".join(map(str, BoardArray[0:63]))
    StrB = "".join(map(str, BoardArray[64:128]))
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
    #If noone won
    return 0

def GenerateChild(State):
    #Generate all child nodes of a given node
    #The check for terminal does not happen within this function, rather before calling this function
    #Takes input directly from Board State, as defined at the beginning of this file

    #Start by picking a piece in the board
    ChildTuple = tuple(copy.deepcopy(State))
    ChildTemp = list(ChildTuple)
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
            ChildTemp[4] += 1
            ChildAll.append(ChildTemp)
            ChildTemp = list(ChildTuple)
            ChildTemp[2] *= -1
        if ChildTemp[0][i] != 7:
            ChildTemp[0][i] += 1 #Applying 'E'
            ChildTemp[4] += 1
            ChildAll.append(ChildTemp)
            ChildTemp = list(ChildTuple)
            ChildTemp[2] *= -1
        if ChildTemp[1][i] != 1:
            ChildTemp[1][i] -= 1 #Applying 'S'
            ChildTemp[4] += 1
            ChildAll.append(ChildTemp)
            ChildTemp = list(ChildTuple)
            ChildTemp[2] *= -1
        if ChildTemp[1][i] != 7:
            ChildTemp[1][i] += 1 #Applying 'N'
            ChildTemp[4] += 1
            ChildAll.append(ChildTemp)
            ChildTemp = list(ChildTuple)
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
    #Now check if anyone won and update accordingly
    for q in range(len(ChildAll)):
        ChildAll[q][3] = TerminalTest(GenerateBoard(ChildAll[q]))
    return ChildAll

def Max_Utility(State,cutoff):
    global TotalStatesExplored 
    Child = GenerateChild(State)
    if State[3] != 0: #If we already are at a leaf node
        PerformanceEval()
        return State
    elif State[4] > cutoff: #Or if we passed the depth limit
        State[3] = Heuristics(State)
        PerformanceEval()
        return State
    utility = - 100 #Technically this needs to be -inf but our utility don't go that far
    for i in range(len(Child)):
        utility = max(utility,Min_Utility(Child[i],cutoff)[3])        
    State[3] = utility
    PerformanceEval()
    return State
    
def Min_Utility(State,cutoff):
    global TotalStatesExplored
    Child = GenerateChild(State)
    if State[3] != 0: #If we already are at a leaf node
        PerformanceEval()
        return State
    elif State[4] > cutoff: #Or if we passed the depth limit
        State[3] = Heuristics(State)
        PerformanceEval()
        return State
    utility = 100 #Technically this needs to be inf but again our utility don't go that far
    for i in range(len(Child)):
        utility = min(utility,Max_Utility(Child[i],cutoff)[3])
    State[3] = utility
    PerformanceEval()
    return State
    
def minmax(State,cutoff):
    #This function applys minmax algorithm to find the next best move, given a step cutoff
    #It returns an action to be taken
    NextBoard = [] #This stores the board after the next best move, with this we can retrack the best action to take
    FindAction = []
    Action = []
    UtilityResults =[]
    Max,Min = 0,1000
    MaxIndex, MinIndex = 0,0
    Child = []
    #First, find the board after the next best move
    Child = GenerateChild(State)
    if State[2] == 1: #Player A's turn
        for i in range(len(Child)):
            UtilityResults.append(Max_Utility(Child[i],cutoff))
            for j in range (len(UtilityResults)):
                if Max < UtilityResults[j][3]:
                    Max = UtilityResults[j][3]
                    MaxIndex = j
            NextBoard = UtilityResults[MaxIndex]
    elif State[2] == -1: #Player B's turn
        for i in range(len(Child)):            
            UtilityResults.append(Min_Utility(Child[i],cutoff))         
            for j in range (len(UtilityResults)):
                if Min > UtilityResults[j][3]:
                    Min = UtilityResults[j][3]
                    MinIndex = j
            NextBoard = UtilityResults[MinIndex]
    #Now backtrack which move causes this board?
    for j in range(12):
        if State[0][j] > NextBoard[0][j]:
            Action.append(str(State[0][j]))
            Action.append(str(State[1][j]))
            Action.append('W')
        elif State[0][j] < NextBoard[0][j]:
            Action.append(str(State[0][j]))
            Action.append(str(State[1][j]))
            Action.append('E')
        elif State[1][j] > NextBoard[1][j]:
            Action.append(str(State[0][j]))
            Action.append(str(State[1][j]))
            Action.append('N')
        elif State[1][j] < NextBoard[1][j]:
            Action.append(str(State[0][j]))
            Action.append(str(State[1][j]))
            Action.append('S')
    return ''.join(Action)

def Heuristics(State):
    #Gives the heuristic evaluation of current state
    return 1

def PerformanceEval():
    global TotalStatesExplored
    TotalStatesExplored += 1
    #print(TotalStatesExplored)


#start_time = time.time()
currentBoard = [[3,7,6,7,7,4,1,4,5,6,3,5],[3,4,5,5,6,7,3,4,5,6,6,7],-1,0,0]       
a = Board(currentBoard)
profile.run('minmax(a.State,1)')
#print(minmax(a.State,2))
#print(TotalStatesExplored)              
#print("--- %s seconds ---" % (time.time() - start_time))