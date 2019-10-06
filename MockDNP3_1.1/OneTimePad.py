###
# Functions that perform XOR gate for one time pad
# Davis Arthur, ORNL
# 7/23/2019
###

from BinaryHexConversions import *

# binStr1, binStr2 - binary strings to convert to integers and perform xor gate
def xor(binStr1, binStr2):

    # make sure that the length of the two binary strings is the same
    # before performing xor
    if len(binStr1) == len(binStr2):

        # convert binary to integers
        num1 = int(binStr1, 2)
        num2 = int(binStr2, 2)

        # perform xor and convert back to binary
        outputInt = num1 ^ num2
        outputBin = intToBinStr(outputInt, len(binStr1))

        return outputBin

    else:
        print("Binary strings are not the same length.")
