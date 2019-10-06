###
# functions for binary/hex/integer conversions
# Davis Arthur, ORNL
# 7/21/19
###

# class turns binary string into an array of octets
# Note: binary string length must be a multiple of 8
def binOctetifier(binString) :

    # delete spaces in binary string
    binString = binString.replace(" ", "")
    length = len(binString)

    # place holder to hold number of octets in octet array
    numOctets = None
    numOctetsDec = length / 8
    numOctetsInt = int(length / 8)
    output = []

    # if the string is divisible by 8 (a string of octets) procede
    if (numOctetsDec == numOctetsInt):
        numOctets = numOctetsInt

        # divide strings into octets and form a list of octets
        i = 0
        while i < numOctets :
            nextOctet = binString[i * 8:i * 8 + 8]
            output.append(nextOctet)
            i += 1

    # if the string is not divisible by 8, alert the user and return empty array
    else :
        print("String not divisible by 8. String has " + str(len(binString)) \
            + " characters")

    return output

# convert binary of any size into hex string
# Note: binary string length must be multiple of 8
def binStringToHex(binString) :
    octets = binOctetifier(binString)
    output = ""
    for octet in octets:
        output += binOctetToHex(octet) + " " # output will be formatted w/space every 2 hex digits
    return output

# turn an integer into a binary string of a any length
def intToBinStr(int, strlen) :
    formatStr = "{0:0" + str(strlen) + "b}"
    return formatStr.format(int)

# turn binary string into array of bytes
# Note: binary string length must be a multiple of 8
def binStringToBytes(bitString) :
    binStringArray = binOctetifier(bitString)
    output = []
    for byte in binStringArray :
        output.append(int(byte, 2))
    output = bytearray(output)
    return output

# convert binary octet to hex
def binOctetToHex(inputOctet) :
    firstfour = inputOctet[0:4]
    lastfour = inputOctet[4:8]
    firstchar = binFourToHex(firstfour)
    secondchar = binFourToHex(lastfour)
    return firstchar + secondchar

# convert binary string of length 4 into single hex digit
def binFourToHex(binFour) :
    num1 = int(binFour[0]) * 8
    num2 = int(binFour[1]) * 4
    num3 = int(binFour[2]) * 2
    num4 = int(binFour[3])
    value = num1 + num2 + num3 + num4
    options = { 0 : zero,
                1 : one,
                2 : two,
                3 : three,
                4 : four,
                5 : five,
                6 : six,
                7 : seven,
                8 : eight,
                9 : nine,
                10 : ten,
                11 : eleven,
                12 : twelve,
                13 : thirteen,
                14 : fourteen,
                15 : fifteen,
    }
    result = options[value]()
    return result

def zero() :
    return "0"

def one() :
    return "1"

def two() :
    return "2"

def three() :
    return "3"

def four() :
    return "4"

def five() :
    return "5"

def six() :
    return "6"

def seven() :
    return "7"

def eight() :
    return "8"

def nine() :
    return "9"

def ten() :
    return "A"

def eleven() :
    return "B"

def twelve() :
    return "C"

def thirteen() :
    return "D"

def fourteen() :
    return "E"

def fifteen() :
    return "F"
