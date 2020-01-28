#Here, state will be a an array of 2 lists, First contain x coordinates of pieces, second contain y coordinates.
#In both arrays, first 6 entries are player A and next 6 are player B. The 3rd, single element of state dictates who is the moving player, 1 for A(X) and -1 for B(O). 
#The 4th element is utility,1 for player A win and -1 for player B win.0 Indicates non-terminal state
#The last element is the current depth in the search tree
import copy
import time
import profile
from random import randint
DefaultBoard = [[1,1,1,7,7,7,1,1,1,7,7,7],[2,4,6,1,3,5,3,5,7,2,4,6],1,0,0]
TotalStatesExplored = 0 #This is used to check the total amount of states explored
UpdateCounter = 0 #This is used to check whether or not our agent find all actions to have equal utility value, therefore effectively not doing anything
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
    PieceNumber = 0
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
        State[2] *= -1
        return State
    else:#Mode 2
        #Create a Child
        ChildNode = [[0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0],0,0,0]
        for i in range(12):
            ChildNode[0][i] = State[0][i]
            ChildNode[1][i] = State[1][i]
        for j in range(2,5):
            ChildNode[j] = State[j]
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
        ChildNode[2] *= -1
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
        return 100
    if BitNumB & BitNumB >> 1 & BitNumB >> 2 & BitNumB >> 3:
        return -100
    #Vertical
    if BitNumA & BitNumA >> 8 & BitNumA >> 16 & BitNumA >> 24:
        return 100
    if BitNumB & BitNumB >> 8 & BitNumB >> 16 & BitNumB >> 24:
        return -100
    #Two kinds of diagnal (right and left, respectively)
    if BitNumA & BitNumA >> 9 & BitNumA >> 18 & BitNumA >> 27:
        return 100
    if BitNumB & BitNumB >> 9 & BitNumB >> 18 & BitNumB >> 27:
        return -100
    if BitNumA & BitNumA >> 7 & BitNumA >> 14 & BitNumA >> 21:
        return 100
    if BitNumB & BitNumB >> 7 & BitNumB >> 14 & BitNumB >> 21:
        return -100
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
      
def Max_Utility(State,cutoff): #Return Utility for player Max (i.e. player A) for MinMax
    global TotalStatesExplored
    array = GenerateBoard(State)
    if State[4] >= cutoff:
        State[3] = Heuristics(State,array)
        PerformanceEval()
        return State[3]
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(array)
        PerformanceEval()
        return State[3]
    utility = - 1000 #Technically this needs to be -inf but our utility don't go that far
    for i in GenerateAction(State,array):
        utility = max(utility, Min_Utility(Update(State,i,2),cutoff))
    PerformanceEval()
    return utility
    
def Min_Utility(State,cutoff): #Return Utility for player Min (i.e. player B) for MinMax
    global TotalStatesExplored
    array = GenerateBoard(State)
    if State[4] >= cutoff:
        State[3] = Heuristics(State,array)
        PerformanceEval()
        return State[3]
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(array)
        PerformanceEval()
        return State[3]
    utility = 1000 #Technically this needs to be inf but our utility don't go that far
    for i in GenerateAction(State,array):
        utility = min(utility, Max_Utility(Update(State,i,2),cutoff))
    PerformanceEval()
    return utility
    
def minmax(State,cutoff):
    #This function applys minmax algorithm to find the next best move, given a step cutoff
    #It returns an action to be taken
    Actions =[]
    MaxArray,MinArray = [],[]
    Max,Min = -1000,1000
    MaxIndex, MinIndex = 0,0
    Actions = GenerateAction(State,GenerateBoard(State))   
    if State[2] == 1: #Player A, so maximize utility
        for i in range(len(Actions)):
            MaxArray.append(Min_Utility(Update(State,Actions[i],2),cutoff))
            if Max < MaxArray[i]:
                Max = MaxArray[i]
                MaxIndex = i
        if len(set(MaxArray)) < 2: #If we have same utility for all actions, generate a random action
            MaxIndex = randint(0,i)
        return Actions[MaxIndex]
    if State[2] == -1: #Player B, so minimize utility
        for j in range(len(Actions)):
            MinArray.append(Max_Utility(Update(State,Actions[j],2),cutoff))
            if Min > MinArray[j]:
                Min = MinArray[j]
                MinIndex = j
        if len(set(MinArray)) < 2: #If we have same utility for all actions, generate a random action
            MinIndex = randint(0,j)
        return Actions[MinIndex]

def AB_Max_Utility(State,cutoff,alpha,beta): #Return Utility for player Max (i.e. player A) for Alpha-Beta
    global TotalStatesExplored
    array = GenerateBoard(State)
    if State[4] >= cutoff:
        State[3] = Heuristics(State,array)
        PerformanceEval()
        return State[3]
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(array)
        PerformanceEval()
        return State[3]
    utility = -1000
    for i in GenerateAction(State,array):
        utility = max(utility, AB_Min_Utility(Update(State,i,2),cutoff,alpha,beta))
        if utility >= beta:
            PerformanceEval()
            return utility
        alpha = max(alpha,utility)
    PerformanceEval()
    return utility

def AB_Min_Utility(State,cutoff,alpha,beta): #Return Utility for player Min (i.e. player B) for Alpha-Beta
    global TotalStatesExplored
    array = GenerateBoard(State)
    if State[4] >= cutoff:
        State[3] = Heuristics(State,array)
        PerformanceEval()
        return State[3]
    if TerminalTest(array) != 0:
        State[3] = TerminalTest(array)
        PerformanceEval()
        return State[3]
    utility = 1000
    for i in GenerateAction(State,array):
        utility = min(utility, AB_Max_Utility(Update(State,i,2),cutoff,alpha,beta))
        if utility <= alpha:
            PerformanceEval()
            return utility
        beta = min(beta,utility)
    PerformanceEval()
    return utility

def alphabeta(State,cutoff,alpha,beta):#Effectively the same as minmax, except that it uses alpha-beta Max and Min
     Action = []
     MaxArray,MinArray = [],[]
     Max,Min = -1000,1000
     MaxIndex, MinIndex = 0,0
     Actions = GenerateAction(State,GenerateBoard(State))
     if State[2] == 1: #Player A, so maximize utility
        for i in range(len(Actions)):
            MaxArray.append(AB_Min_Utility(Update(State,Actions[i],2),cutoff,alpha,beta))
            if Max < MaxArray[i]:
                Max = MaxArray[i]
                MaxIndex = i
        if len(set(MaxArray)) < 2: #If we have same utility for all actions, generate a random action
            MaxIndex = randint(0,i)
        return Actions[MaxIndex]
     if State[2] == -1: #Player B, so minimize utility
        for j in range(len(Actions)):
            MinArray.append(AB_Max_Utility(Update(State,Actions[j],2),cutoff,alpha,beta))
            if Min > MinArray[j]:
                Min = MinArray[j]
                MinIndex = j
        if len(set(MinArray)) < 2: #If we have same utility for all actions, generate a random action
            MinIndex = randint(0,j)
        return Actions[MinIndex]

def Heuristics(State,array):
    #Gives the heuristic evaluation of current state
    #It's worth explaining a bit the "scoring" system I used here: for a known win/lose situation, utility is 100 for black win and -100 for white win.
    #For any cases in between, favorable situations for black result in + points, whereas favorable for white result in - points. The final point is then evaluated

    StrA = "".join(map(str, array[0:63]))
    StrB = "".join(map(str, array[64:128]))
    BitNumA = int(StrA,base = 2)
    BitNumB = int(StrB,base = 2)
    BitTotal = BitNumA | BitNumB
    score = 0 
    #It's ok to have a score of 0, even though you might think this leads to the system consider game unfinished, because only when TerminalTest checked the game was finished will the program assign heuristic points
    #We check for consecutive pieces already, with empty spaces following (so there is enough room for potential connection of 4). 
    #Note here we only count1 set of connected pieces. More sets cause the agent to favor a cross-shaped configuration
    #2 pieces:
    if BitNumA & BitNumA >> 1: #Horizontal
        score += 5        
    elif BitNumA & BitNumA >> 8: #Vertical
        score += 5
    elif BitNumA & BitNumA >> 9: #Diagonal
        score += 5
    elif BitNumA & BitNumA >> 7: #Also diagonal
        score += 5
    if BitNumB & BitNumB >> 1:
        score -= 5        
    elif BitNumB & BitNumB >> 8:
        score -= 5
    elif BitNumB & BitNumB >> 9:
        score -= 5
    elif BitNumB & BitNumB >> 7:
        score -= 5
    #3 pieces:
    if BitNumA & BitNumA >> 1 & BitNumA >> 2: 
        score += 10
    elif BitNumA & BitNumA >> 8 & BitNumA >> 16: 
        score += 10
    elif BitNumA & BitNumA >> 9 & BitNumA >> 18: 
        score += 10
    elif BitNumA & BitNumA >> 7 & BitNumA >> 14: 
        score += 10
    if BitNumB & BitNumB >> 1 & BitNumB >> 2:
        score -= 10             
    elif BitNumB & BitNumB >> 8 & BitNumB >> 16:
        score -= 10
    elif BitNumB & BitNumB >> 9 & BitNumB >> 18:
        score -= 10
    elif BitNumB & BitNumB >> 7 & BitNumB >> 14:
        score -= 10
    return score

def PerformanceEval():
    global TotalStatesExplored
    TotalStatesExplored += 1
    #print(TotalStatesExplored)

def PlayGame(Board): #Create a interactive game UI
    array = GenerateBoard(Board.State)
    player = int(input('Please indicate whether you play X(type 1) or O(type 2).\n'))
    Finished = 0
    explored = []
    while Finished == 0:
        GenerateGraph(array)
        if (player == 2 and Board.State[2] == -1) or (player == 1 and Board.State[2] == 1):
            print('Your turn.')
            Action = input('Type in your move: \n')
            Board.State = Update(Board.State,Action,1) 
        else:
            Action = alphabeta(a.State,6,-1000,1000)
            #Action = minmax(a.State,4)
            print('My move is ',Action,'\n')
            Board.State = Update(Board.State,Action,1)        
        array = GenerateBoard(Board.State)
        Finished = TerminalTest(array)
        if Finished != 0:
            print('Game has finished!\n')
            GenerateGraph(array)
            if Finished > 0:
                print('Player X (black) won! \n')
            else:
                print('Player O (white) won! \n')
            break



#profile.run('minmax(a.State,1)')

cB1 = [[3,7,6,7,7,4,1,4,5,6,3,5],[3,4,5,5,6,7,3,4,5,6,6,7],-1,0,0]
cB2 = [[1,3,3,2,6,7,1,2,4,5,6,1],[2,3,4,6,5,4,1,1,4,5,3,7],-1,0,0]
cB3 = [[3,3,3,5,5,5,3,3,3,5,5,5],[3,4,7,1,2,6,1,2,6,3,5,7],-1,0,0]
cBtest = [[3,7,6,7,7,4,7,1,7,6,3,5],[3,4,3,5,6,7,2,4,7,6,6,7],1,0,0]
a = Board(cB3)
PlayGame(a)

#profile.run('minmax(a.State,4)')   
#start_time = time.time()
#print(minmax(a.State,4))           
#print("--- %s seconds ---" % (time.time() - start_time))
#print(TotalStatesExplored)