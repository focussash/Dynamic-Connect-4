import socket
import copy
import time
import profile
from random import randint
DefaultBoard = [[1,1,1,7,7,7,1,1,1,7,7,7],[2,4,6,1,3,5,3,5,7,2,4,6],-1,0,0]
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
        #Now,change player
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
    #Move ordering based on heuristics; I commented out these because they take too much computing time
    #utilities =[]
    #for j in range(len(Action)):
    #    utilities.append(Heuristics(Update(State,Action[j],2),BoardArray))
    #if State[2] == 1:
    #    Action = [x for _,x in sorted(zip(utilities,Action))]
    #else:
    #    Action = [x for _,x in sorted(zip(utilities,Action),reverse = True)]
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
        State[3] = TerminalTest(array)+ State[2]*State[4]#We substract a tiny bit off as a penatly for going far.I.e. if you can win earlier, dont do it later
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
        State[3] = TerminalTest(array)+ State[2]*State[4]#We substract a tiny bit off as a penatly for going far.I.e. if you can win earlier, dont do it later
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
        State[3] = TerminalTest(array) + State[2]*State[4]#We substract a tiny bit off as a penatly for going far.I.e. if you can win earlier, dont do it later
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
        State[3] = TerminalTest(array)+ State[2]*State[4]#We substract a tiny bit off as a penatly for going far.I.e. if you can win earlier, dont do it later
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
        #print('Utility of chosen move is: ',Max)
        return Actions[MaxIndex]
     if State[2] == -1: #Player B, so minimize utility
        for j in range(len(Actions)):
            MinArray.append(AB_Max_Utility(Update(State,Actions[j],2),cutoff,alpha,beta))
            if Min > MinArray[j]:
                Min = MinArray[j]
                MinIndex = j
        if len(set(MinArray)) < 2: #If we have same utility for all actions, generate a random action
            MinIndex = randint(0,j)
        #print('Utility of chosen move is: ',Min)
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
    distance = 0
    score = 0 
    #It's ok to have a score of 0, even though you might think this leads to the system consider game unfinished, because only when TerminalTest checked the game was finished will the program assign heuristic points
    #We check for consecutive pieces already, with empty spaces following (so there is enough room for potential connection of 4). 
    #Note here we only count1 set of connected pieces. More sets cause the agent to favor a cross-shaped configuration
    #2 pieces:
    if BitNumA & BitNumA >> 1: #Horizontal
        score += 5       
    if BitNumA & BitNumA >> 8: #Vertical
        score += 5
    if BitNumA & BitNumA >> 9: #Diagonal
        score += 5
    if BitNumA & BitNumA >> 7: #Also diagonal
        score += 5
    if BitNumB & BitNumB >> 1:
        score -= 5        
    if BitNumB & BitNumB >> 8:
        score -= 5
    if BitNumB & BitNumB >> 9:
        score -= 5
    if BitNumB & BitNumB >> 7:
        score -= 5
    #3 pieces:
    if BitNumA & BitNumA >> 1 & BitNumA >> 2: 
        score += 10
    if BitNumA & BitNumA >> 8 & BitNumA >> 16: 
        score += 10
    if BitNumA & BitNumA >> 9 & BitNumA >> 18: 
        score += 10
    if BitNumA & BitNumA >> 7 & BitNumA >> 14: 
        score += 10
    if BitNumB & BitNumB >> 1 & BitNumB >> 2:
        score -= 10             
    if BitNumB & BitNumB >> 8 & BitNumB >> 16:
        score -= 10
    if BitNumB & BitNumB >> 9 & BitNumB >> 18:
        score -= 10
    if BitNumB & BitNumB >> 7 & BitNumB >> 14:
        score -= 10
    #Another heuristic we can include is to calculate the max distance between pieces for each player
    #Note that more attributes are given for x-axis distance, because from the starting board this distance is the farthest and needs to be handled
    distance += (max(State[0][0:6]) - min(State[0][0:6]))*7 + (max(State[1][0:6]) - min(State[1][0:6]))*2
    distance -= (max(State[0][6:12]) - min(State[0][6:12]))*7 + (max(State[1][6:12]) - min(State[1][6:12]))*2 #For a given player, the more distance between pieces of his opponent, the better.
    score -= distance * State[2]
    #Lastly, we care about step depth: if we could reach the same state with less moves, dont do more
    score -= State[2]*State[4]
    #Now if we get a utility higher than winning, we need to cut it down (because it is NOT better than winning)
    while score >= 100 or score <= -100:
        score -= 10 * State[2]
    return score

def PerformanceEval():
    global TotalStatesExplored
    TotalStatesExplored += 1
    #print(TotalStatesExplored)

def PlayGame(Board): #Create a interactive game UI
    global TotalStatesExplored
    array = GenerateBoard(Board.State)
    player = int(input('Please indicate whether you play X(type 1) or O(type 2).\n'))
    cutoff = int(input('Please indicate depth cutoff.\n'))
    Finished = 0
    while Finished == 0:
        GenerateGraph(array)
        if (player == 2 and Board.State[2] == -1) or (player == 1 and Board.State[2] == 1):
            print('Your turn.')
            Action = input('Type in your move: \n')
            Board.State = Update(Board.State,Action,1) 
        else: #Uncomment one of the following two lines to select different search algorithms
            TotalStatesExplored = 0
            Action = alphabeta(Board.State,cutoff,-1000,1000)
            #Action = minmax(Board.State,cutoff)
            print('My move is ',Action,'\n')
            print('Depth cutoff is: ',cutoff)
            print('Total amount of nodes explored is: ',TotalStatesExplored)
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


def client(Board): #This is for interacting with the java server
    player = 0
    Finished = 0
    Action =[]
    ActionReceived =[]
    #The following 4 parameters will be subject to the actual game
    host = input('Please input host address:\n')
    port = int(input('Please input port number:\n'))
    gameID = input('Please input game ID:\n')
    color = input('Please input color this agent will play:\n')
    ad = (host,port)
    string =[]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating a socket object. This piece of code is copied from online tutorial
    sock.connect(ad)
    string = str(gameID)+ ' '+ color +'\n'
    bmsg = string.encode('utf-8') #Everytime we send or read, need to encode from/to string to/from object type "byte"
    sock.sendall(bmsg)
    if color == 'black':
        player = 1
    else:
        player = -1
    array = GenerateBoard(Board.State)
    sock.recv(4096).decode("utf-8")
    while Finished == 0:
        GenerateGraph(array)
        if (player == 1 and Board.State[2] == -1) or (player == -1 and Board.State[2] == 1):
            print('Your turn.')
            try:
                ActionReceived = sock.recv(4096).decode("utf-8")
                if ActionReceived[0] == 'T':
                    print('Oops, timed out')
                    break;
            except:
                print('Connection Issue')
            Action = ActionReceived
            Board.State = Update(Board.State,Action,1) 
        else: #Uncomment one of the following two lines to select different search algorithms
            Action = alphabeta(Board.State,4,-1000,1000)
            #Action = (minmax(board.State,3)
            string = Action + '\n'
            bmsg = string.encode('utf-8')
            sock.sendall(bmsg)
            try:
                ActionReceived = sock.recv(4096).decode("utf-8")
                if ActionReceived[0] == 'T':
                    print('Oops, timed out')
                    break;
            except:
                print('Connection Issue')
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
            sock.close()
            break



#Here, state will be a an array of 2 lists, First contain x coordinates of pieces, second contain y coordinates.
#In both arrays, first 6 entries are player A and next 6 are player B. The 3rd, single element of state dictates who is the moving player, 1 for A(X) and -1 for B(O). 
#The 4th element is utility,1 for player A win and -1 for player B win. 0 Indicates non-terminal state
#The last element is the current depth in the search tree

#Sample State: State = [[1,1,1,7,7,7,1,1,1,7,7,7],[2,4,6,1,3,5,3,5,7,2,4,6],-1,0,0]
#This gives the initial board as defined in the assignment, with white playing first

#The following 3 boards are the boards as given in assignment, for evaluation of performance
cB1 = [[3,7,6,7,7,4,1,4,5,6,3,5],[3,4,5,5,6,7,3,4,5,6,6,7],-1,0,0]
cB2 = [[1,3,3,2,6,7,1,2,4,5,6,1],[2,3,4,6,5,4,1,1,4,5,3,7],-1,0,0]
cB3 = [[3,3,3,5,5,5,3,3,3,5,5,5],[3,4,7,1,2,6,1,2,6,3,4,7],-1,0,0]
cB4 = [[3,7,6,7,7,4,1,4,5,6,3,6],[3,4,3,5,6,7,3,4,5,6,6,7],-1,0,0]

#If trying to play by initial board, you dont need to give State argument
board = Board()#Input state as argument if want to try different state. Whichever of the following "modes" you use, this line needs to be run
#PlayGame(board) #Run this if want to interactively play with agent. 
client(board)   #Runthis if want to play via server

#start_time = time.time()                     #Uncomment this line and line 437 if you want to know run time. But dont do this if playing interactively or against another agent
#profile.run('alphabeta(board.State,6,-1000,1000)')
#print(alphabeta(board.State,5,-1000,1000))       #Run this if want to give a result of alphabeta pruning with state and depth cutoff  
#print(minmax(board.State,3))                      #Run this if want to give a result of minmax with state and depth cutoff 
#print("--- %s seconds ---" % (time.time() - start_time))
#print(TotalStatesExplored)                   #Run this along with either of the previous 2 commands to print the amount of states explored
