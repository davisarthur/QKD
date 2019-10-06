###
# Functions to calculate the QBER on sifted keys even if the theoretical QBER
# is higher than the threshold for secure secret key exchange
# Davis Arthur, ORNL
# 7/31/2019
###
from get_id3100_keys import *

def readSiftedKeys():

    # read in Alice's sifted key file
    aliceFile = input("Enter Alice's sifted key file: ")
    aliceKeyTable = initial_load(aliceFile)
    aliceKeys = aliceKeyTable[1]

    # read in Bob's sifted key file
    bobFile = input("\nEnter Bob's sifted key file: ")
    bobKeyTable = initial_load(bobFile)
    bobKeys = bobKeyTable[1]

    # construct string with Alice's entire key
    aliceFullKey = ""

    for key in aliceKeys:
        aliceFullKey += str(key)

    # construct string with Bob's entire key
    bobFullKey = ""

    for key in bobKeys:
        bobFullKey += str(key)

    return (aliceFullKey, bobFullKey)

def compareKeys(aliceKey, bobKey):

    keyLength = len(aliceKey)
    indexes = range(keyLength)

    # compare each character in the full key
    errorCount = 0
    for i in indexes:
        if aliceKey[i] != bobKey[i]:
            errorCount += 1

    # calculate QBER
    qber = errorCount / keyLength

    return qber

def main():

    aliceKey, bobKey = readSiftedKeys()
    qber = compareKeys(aliceKey, bobKey)
    print("\nQBER = " + str(qber))

# test
main()
