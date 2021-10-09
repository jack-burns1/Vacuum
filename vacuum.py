#  Jack Burns
#  vacuum.py
#  

import random

# Tree evaluation performed here based on black board
def roomba(bBoard):
    #create a list for every sequence and priority
    seq1_obj, seq2_obj, seq3_obj, seq4_obj, seq5_obj, p1_obj, p2_obj, sel_obj = (
        ([] for i in range(8)))

    # Building tree structure
    seq1_obj.extend([Battery(bBoard), FindHome(bBoard), GoHome(bBoard), Dock(bBoard)])
    seq2_obj.extend([Spot(bBoard), Timer(bBoard, CleanSpot(bBoard), 20), DoneSpot(bBoard)])
    seq5_obj.extend([DustySpot(bBoard), Timer(bBoard, CleanSpot(bBoard), 35)])
    p2_obj.extend([Sequence(seq5_obj, bBoard), UntilFails(bBoard, CleanFloor(bBoard))])
    seq4_obj.extend([Priority(bBoard, p2_obj), DoneGeneral(bBoard)])
    seq3_obj.extend([GeneralCleaning(bBoard), Sequence(seq4_obj, bBoard)])
    sel_obj.extend([Sequence(seq2_obj, bBoard), Sequence(seq3_obj, bBoard)])
    p1_obj.extend([Sequence(seq1_obj, bBoard), Selection(sel_obj, bBoard), DoNothing(bBoard)])

    head = Priority(bBoard, p1_obj)
    runtime = "true"
    updateTime = 0

    # main running loop
    # runs until the user 
    while runtime == "true":
        bBoard[6] = head.run()
        bBoard[0] -= 1

        updateTime += 1
        #ask user if they want spot/general cleaning again
        if updateTime >= 50 and bBoard[2] == "false" and bBoard[2] == "false":
            updateTime = 0
            runtime = input("Do you want to keep running the roomba? (true/false) ").lower()

            if runtime == "true":
                askUser(bBoard)

#set initial values of the black board
#only called once at the start of program
def setBlackBoard():
    # Key:  [      0      ,       1      ,         2       ,      3     ,    4    ,   5  ,   6  ] 
    # Value:[BATTERY_LEVEL, SPOT_CLEANING, GENERAL_CLEANING, DUSTY_SPOT, HOME_PATH, TIMER, STATE]
    blackBoard = [0, "false", "false", "false", "none", 0, "SUCCEEDED"] 
    blackBoard[0] = int(input("What is the current batery level? (%): ")) % 100

    askUser(blackBoard)
    return blackBoard

#Populate manual entries in the black board by asking user
def askUser(bBoard):
    bBoard[1] = input("Do you want to spot clean? (true/false): ").lower() 
    bBoard[2] = input("Do you want general cleaning? (true/false): ").lower()
    foundDustySpot(bBoard)

#Randomly detrmine if the roomba detected a dusty spot
def foundDustySpot(bBoard):
    sensor = random.randrange(1, 10, 1)

    if sensor >= 8:
        print("Dusty Spot Detected!")
        bBoard[3] = "true"
    else:
        bBoard[3] = "false"

#Fails if one child fails
# takes in a list of node objects
class Sequence:
    def __init__(self, children, bBoard):
        self.children = children
        self.bBoard = bBoard

    def run(self):
        for i in self.children:
            res = i.run()
            if res == "FAILED":
                return "FAILED"

            elif res == "RUNNING":
                return "RUNNING"
            
        return "SUCCEEDED"  

# Fails if all children fail
# takes in a list of node objects
class Selection:
    def __init__(self, children, bBoard):
        self.bBoard = bBoard
        self.children = children

    def run(self):
        for i in self.children:
            res = i.run()
            if res == "SUCCEEDED":
                return "SUCCEEDED"

            elif res == "RUNNING":
                return "RUNNING"

        return "FAILED"

# Conditional check if battery is below 30
class Battery:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        if self.bBoard[0] < 30:
            return "SUCCEEDED"
        else:
            return "FAILED"

# Updates home path in black board
class FindHome:
    def __init__(self, bBboard):
        self.bBoard = bBoard

    def run(self):
        self.bBoard[4] = "FOUND HOME PATH"
        return "SUCCEEDED"

# Uses black board value to move home
class GoHome:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        if self.bBoard[4] != "none":
            #move to bBoard[4] (home path) if not already there
            return "SUCCEEDED"
         
        return "FAILED"

# Docks the roomba for 3 seconds
class Dock:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        # If simulation starts with battery under 30%, it cannot be RUNNING
        # If a task makes battery fall below 30%, battery will be at 29% on first instance
        if self.bBoard[6] != "RUNNING" or self.bBoard[0] == 29:
            self.bBoard[5] = 3

        self.bBoard[5] -= 1
        print("Docking...")

        if self.bBoard[5] == 0:
            self.bBoard[0] = 100        #fully charge battery
            return "SUCCEEDED"

        return "RUNNING"

# Check if spot cleaning was requested
class Spot:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        if self.bBoard[1] == "true":
            return "SUCCEEDED"
        
        return "FAILED"

# Do spot cleaning activities
class CleanSpot:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
       print("Cleaning Spot...")
       return "SUCCEEDED"

# Tell black board you're done spot cleaning
class DoneSpot:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        self.bBoard[1] = "false"    #DONE SPOT = false
        return "SUCCEEDED"

# Ask black board if it detected a dusty spot
class DustySpot:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        if self.bBoard[3] == "false":
            return "FAILED"

        return "SUCCEEDED"

# Set the timer value in the black board to the given time if necessary
# Run the given node, and decrease the time.
class Timer:
    def __init__(self, bBoard, obj, time):
        self.bBoard = bBoard
        self.obj = obj
        self.time = time

    def run(self):
        if self.bBoard[6] != "RUNNING":
            self.bBoard[5] = self.time + 1

        if self.obj.run() == "FAILED":
            return "FAILED"

        self.bBoard[5] -= 1
        if self.bBoard[5] != 0:
            return "RUNNING"
        
        return "SUCCEEDED"

# Fails if all children fail
# takes in a list of node objects, and evaluates them in specific order
class Priority:
    def __init__(self, bBoard, sortedChildren):
        self.bBoard = bBoard
        self.sortedChildren = sortedChildren

    def run(self):
        for i in self.sortedChildren:
            res = i.run()

            if res == "SUCCEEDED":
                return "SUCCEEDED"
            if res == "RUNNING":
                return "RUNNING"
            
        return "FAILED"

# Performs general cleaning activities
class GeneralCleaning:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        if self.bBoard[2] == "false":
            return "FAILED"

        return "SUCCEEDED"

# Performs floor cleaning activities
class CleanFloor:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        print("Cleaning Floor...")
        done = random.randrange(1, 100, 1)
        # Randomly decides if task is finished (95% chance of still running)
        if done >= 95:
            return "FAILED"
        
        return "SUCCEEDED"

# Runs the given node, and returns running if the task did not succeed.
class UntilFails:
    def __init__(self, bBoard, obj):
        self.bBoard = bBoard
        self.obj = obj

    def run(self):
        res = self.obj.run()
        if res == "SUCCEEDED":
            return "RUNNING"
            
        if res == "FAILED":
            return "SUCCEEDED"

# Updates black board to set general cleaning to false
class DoneGeneral:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        self.bBoard[2] = "false"

# Prints that the roomba is doing nothing
class DoNothing:
    def __init__(self, bBoard):
        self.bBoard = bBoard

    def run(self):
        print("Doing Nothing...")
        return "SUCCEEDED"

bBoard = setBlackBoard()
roomba(bBoard)