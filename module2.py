#Here, state will be a an array of 2 lists, First contain x coordinates of pieces, second contain y coordinates.
#In both arrays, first 6 entries are player A and next 6 are player B. The 3rd, single element of state dictates who is the moving player, 1 for A(X) and -1 for B(O). 
#The 4th element is utility,1 for player A win and -1 for player B win.0 Indicates non-terminal state
#The last element is the current depth in the search tree
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


def Update(State,Action,Mode):
    #Mode 1: Apply an action (moving one piece) to update the current board, reflecting a move done by either the agent or opponent
    #Mode 2: Create a new ChildState of the current board, used for searching solutions
    X = int(Action[0])
    Y = int(Action[1])
    Act = Action[2]       
    if Mode == 1:
        #Now, find the piece to update
        for x in range(12):
            if State[0][x] == X and State[1][x] == Y:
                PieceNumber = x
        #Now, update the corresponding piece
        if Act == 'N':
            State[1][PieceNumber] -= 1
        elif Act == 'S':
            State[1][PieceNumber] += 1
        elif Act == 'E':
            State[0][PieceNumber] += 1
        elif Act == 'W':
            State[0][PieceNumber] -= 1
        #Now,update depth and change player
        State[4] += 1
        State[3] *= -1
        return State
    else:
        #Create a Child
        ChildNode = copy.deepcopy(State)
        #Then, do the update on the child node
        for x in range(12):
            if ChildNode[0][x] == X and ChildNode[1][x] == Y:
                PieceNumber = x
        #Now, update the corresponding piece
        if Act == 'N':
            ChildNode[1][PieceNumber] -= 1
        elif Act == 'S':
            ChildNode[1][PieceNumber] += 1
        elif Act == 'E':
            ChildNode[0][PieceNumber] += 1
        elif Act == 'W':
            ChildNode[0][PieceNumber] -= 1
        #Now,update depth and change player
        ChildNode[4] += 1
        ChildNode[3] *= -1
        return ChildNode
        
def GenerateBoard(State):
    #This generates a bitboard of the current board (an array of 8*8 binary numbers; the bottom row and rightmost column are all 0s to avoid TerminalTest errors)
    BoardArrayA = [0]*64
    BoardArrayB = [0]*64
    for k in range(6):
        BoardArrayA[State[0][k]-1 + 8* (State[1][k]-1)] = 1
    for k in range(6,12):
        BoardArrayB[State[0][k]-1 + 8* (State[1][k]-1)] = 1 
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

def GenerateAction(State,BoardArray):
    #Generate all valid actions to apply on a given node
    #The check for terminal does not happen within this function, rather before calling this function
    #Takes input directly from Board State, as defined at the beginning of this file
    Action = []
    temp = []
    #Start by picking a piece in the board for current player
    if State[2] == 1:
        player = range(6)
    else:
        player = range(6,12)
    #For each piece, check 1)whether it's at a border 2) whether it has a neighbouring piece
    for i in player:
        if State[0][i]-1 and not(BoardArray[State[0][i]-2 + 8* (State[1][i]-1)] or BoardArray[State[0][i]-2 + 8* (State[1][i]-1)+64]): 
            temp = [State[0][i],State[1][i],'W']
            Action.append(''.join(map(str,(temp))))
        if State[0][i]-7 and not(BoardArray[State[0][i] + 8* (State[1][i]-1)] or BoardArray[State[0][i] + 8* (State[1][i]-1)+64]): 
            temp = [State[0][i],State[1][i],'E']
            Action.append(''.join(map(str,(temp))))
        if State[1][i]-1 and not(BoardArray[State[0][i]-1 + 8* (State[1][i]-2)] or BoardArray[State[0][i]-1 + 8* (State[1][i]-2)+64]): 
            temp = [State[0][i],State[1][i],'N']
            Action.append(''.join(map(str,(temp))))
        if State[1][i]-7 and not(BoardArray[State[0][i]-1 + 8* (State[1][i])] or BoardArray[State[0][i]-1 + 8* (State[1][i])+64]): 
            temp = [State[0][i],State[1][i],'S']
            Action.append(''.join(map(str,(temp))))
    return Action
    #For each piece, check if it has a neighbouring piece
               
        
      
def Max_Utility(State,cutoff):
    global TotalStatesExplored 
    if State[4] == cutoff:
        State[3] = Heuristics(State)
        PerformanceEval()
        return State[3]
    array = GenerateBoard(State)
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(GenerateBoard(State))
        PerformanceEval()
        return State[3]
    utility = - 100 #Technically this needs to be -inf but our utility don't go that far
    for i in GenerateAction(State,array):
        utility = max(utility, Min_Utility(Update(State,i,2),cutoff))
    PerformanceEval()
    return utility
    
def Min_Utility(State,cutoff):
    global TotalStatesExplored
    if State[4] == cutoff:
        State[3] = Heuristics(State)
        PerformanceEval()
        return State[3]
    array = GenerateBoard(State)
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(GenerateBoard(State))
        PerformanceEval()
        return State[3]
    utility = 100 #Technically this needs to be inf but our utility don't go that far
    for i in GenerateAction(State,array):
        utility = min(utility, Max_Utility(Update(State,i,2),cutoff))
    PerformanceEval()
    return utility
    
def minmax(State,cutoff):
    #This function applys minmax algorithm to find the next best move, given a step cutoff
    #It returns an action to be taken
    Actions =[]
    Max,Min = 0,1000
    MaxIndex, MinIndex = 0,0
    Child = []
    #First, find the board after the next best move
    Actions = GenerateAction(State,GenerateBoard(State))
    if State[2] == 1: #Player A, so maximize utility
        for i in range(len(Actions)):
            if Max < Min_Utility(Update(State,Actions[i],2),cutoff):
                Max = Min_Utility(Update(State,Actions[i],2),cutoff)
                MaxIndex = i
        return Actions[MaxIndex]
    if State[2] == -1: #Player B, so minimize utility
        for j in range(len(Actions)):
            if Min > Max_Utility(Update(State,Actions[j],2),cutoff):
                Min = Max_Utility(Update(State,Actions[j],2),cutoff)
                MinIndex = j
        return Actions[MinIndex]
    
def Heuristics(State):
    #Gives the heuristic evaluation of current state
    return 1

def PerformanceEval():
    global TotalStatesExplored
    TotalStatesExplored += 1
    #print(TotalStatesExplored)

#profile.run('minmax(a.State,1)')

#start_time = time.time()
cB = [[3,7,6,7,7,4,1,4,5,6,3,5],[3,4,5,5,6,7,3,4,5,6,6,7],-1,0,0]       
a = Board(cB)
profile.run('minmax(a.State,3)')
#print(minmax(a.State,6))
print(TotalStatesExplored)              
#print("--- %s seconds ---" % (time.time() - start_time))
