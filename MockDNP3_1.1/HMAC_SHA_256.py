###
# Function performs HMAC-SHA256 algorithm on DNP3 challenge data
# Davis Arthur
# 7/11/2019
###

import hmac
from BinaryHexConversions import *

# challengeDataString — challenge data from authentication challenge
# keyString — symmetric key as binary string
# truncate — truncates the resulting mac value to the leftmost ___ octets
# returns mac value as binary string 
def challenge(challengeDataString, keyString, truncate = 16) :

    print("Key used for HMAC-SHA256: " + keyString)
    print("Challenge data used for HMAC-SHA256: " + challengeDataString)

    # convert key and challenge data to bytes
    key = binStringToBytes(keyString)
    challengeData = binStringToBytes(challengeDataString)

    # create hmacObj and compute mac value
    hmacObj = hmac.new(key, challengeData, "sha256")
    macValueBytes = hmacObj.digest()

    # convert and store the mac value as a binary string
    macValueBinary = ""

    for byte in macValueBytes :
        macValueBinary += intToBinStr(byte, 8)

    # truncate the mac value
    macValueBinary = macValueBinary[0:truncate * 8]
    print("Truncated MAC value: " + macValueBinary)

    return macValueBinary
