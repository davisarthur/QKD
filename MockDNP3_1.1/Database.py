###
# Class to define databases in DNP3 outstations and master stations
# Davis Arthur, ORNL
# 7/22/19
###

import random

class Database:

    # column size - length of each point column in DNP3 database
    def __init__(self, colSize = 10):
        # initialize each column entry as 0
        self.binaryInput = [0] * colSize
        self.analogInput = [0] * colSize
        self.counterInput = [0] * colSize
        self.binaryOutput = [0] * colSize
        self.analogOutput = [0] * colSize
        # table holds each column
        self.table = [self.binaryInput, self.analogInput, self.counterInput, \
            self.binaryOutput, self.analogOutput]

    # this method fills the given column with pseudo-random numbers
    def randomizeCol(self, col) :

        sizeOfCol = len(self.table[col])
        newColumn = []
        for i in range(sizeOfCol):
            newColumn.append(random.randint(1, 100))
        self.table[col] = newColumn

    # returns a value from the database table by specifying column and index
    def getVal(self, col, index) :
        return self.table[col][index]

    # set a value in the database table
    def setVal(self, col, row, value) :
        self.table[col][row] = value
