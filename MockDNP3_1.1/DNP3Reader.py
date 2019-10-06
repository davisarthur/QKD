###
# functions used to read in DNP3 messages in binary
# Davis Arthur, ORNL
# 7/22/2019
###

from ApplicationLayer import *
from RangeField import *

# reads in a portion of a string
# startIndex - index of first desired character
# message - string to read from
# length - number of characters to read
# returns newIndex - the index of the last character read
# returns outputStr - the string that was read
def read(startIndex, message, length = 8):
    outputStr = message[startIndex:startIndex + length]
    newIndex = startIndex + length
    return (newIndex, outputStr)

# reads in the application header of a response message
# message - string to read from
# returns index - index where the function quit reading
# returns returnObj - read in application response header
def readAppResHeader(message):

    # get application control octet
    index, appControlOctet = read(0, message)
    print("Application Control Octet: " + appControlOctet)

    # get function code
    index, functionCode = read(index, message)
    print("Function Code: " + functionCode)

    # get internal indications; for the sake of demonstration, all internal
    # indications should be defualt
    index, internalIndications = read(index, message, 16)
    print("Internal Indications: " + internalIndications)

    # intialize app header of function code 0
    returnObj = AppResHeader(0)

    # set the app control and function code according to read in data
    returnObj.applicationControl = appControlOctet
    returnObj.functionCode = functionCode

    return (index, returnObj)

# reads in application request header
# message - string to read from
# returns index - index where the function quit reading
# returns returnObj - read in application request header
def readAppHeader(message):

    # get application control octet
    index, appControlOctet = read(0, message)
    print("Application Control Octet: " + appControlOctet)

    # get function code
    index, functionCode = read(index, message)
    print("Function Code: " + functionCode)

    # initialize app header of function code 0
    returnObj = AppHeader(0)

    # set the app control and function code according to read in data
    returnObj.applicationControl = appControlOctet
    returnObj.functionCode = functionCode

    return (index, returnObj)


# reads in object header from DNP3 message
# startIndex - index to begin reading from
# message - string to read from
# returns index - index where the function quit reading
# returns returnObj - read in object header
def readObjHeader(startIndex, message):

    # get the group, variation, and qualifier of the objects under the header
    index, objHeaderGroup = read(startIndex, message)

    # if there is no header, return None
    if(objHeaderGroup == ""):
        return index, None

    index, objHeaderVar = read(index, message)
    index, objHeaderQual = read(index, message)

    # get the object header prefix code and range specifier code from object
    # header qualifier
    objHeaderPre = objHeaderQual[1:4]
    objHeaderRangeSpec = objHeaderQual[4:8]

    print("Object Group: " + objHeaderGroup)
    print("Object Variation: " + objHeaderVar)
    print("Object prefix code: " + objHeaderPre)
    print("Range Specifier: " + objHeaderRangeSpec)

    # determine range field size from rangespec code
    rangeFieldSize = 0

    # if the range specifier code is 0, then the range field is 2 octets
    if objHeaderRangeSpec == intToBinStr(0, 4):
        rangeFieldSize = 2 * 8

    # if the range specifier code is 11 or 7, then the range field is 1 octet
    elif objHeaderRangeSpec == intToBinStr(11, 4) or objHeaderRangeSpec == intToBinStr(7, 4):
        rangeFieldSize = 8 # size of authentication range fields

    else:
        print("Error: Range specifier does not match sample types")

    # read in and print the range field of the object header
    index, rangeFieldStr = read(index, message, rangeFieldSize)
    objHeaderRangeField = RangeField(0, 0, 0, rangeFieldStr)
    print("Range Field: " + str(objHeaderRangeField))

    # create an object header object from the data that was read in
    objHeader = ObjHeader(int(objHeaderGroup, 2), int(objHeaderVar, 2), \
        int(objHeaderPre, 2), int(objHeaderRangeSpec, 2), objHeaderRangeField)

    return (index, objHeader)

# reads in objects under an object header from DNP3 message
# startIndex - index to begin reading from
# message - string to read from
# returns index - index where the function quit reading
# returns returnObj - read in objects list
def readObjs(startIndex, objsHeader, message):

    # placeholder for prefix length in octets
    prefixType = -1

    # if object prefix is 000, then the prefix is 0 bits
    if objsHeader.objpre == intToBinStr(0, 3):
        prefixType = 0

    # if object prefix is 101 (code 5), then the prefix is 2 octets
    elif objsHeader.objpre == intToBinStr(5, 3):
        prefixType = 2

    # if object prefix does not match sample prefix codes, produce error
    else:
        print("Error: object prefix does not match sample types")
        return None

    # placeholders for the length of each object and the number of objects in list
    objectLength = 0
    numOfObjects = objsHeader.rangeField.numOfObjects

    # is the object an authentication object?
    isAuthentication = (objsHeader.group == intToBinStr(120, 8))
    hasSetLength = not isAuthentication

    # if the objects are of group 30 var 2, objs are analog and 24 bits long
    if objsHeader.group == intToBinStr(30, 8):
        if objsHeader.variation == intToBinStr(2, 8):
            objectLength = 24

    # if the objects are of group 120 var 4 (key status request), the object is
    # 16 bits long
    elif isAuthentication:
        if objsHeader.variation == intToBinStr(4, 8):
            objectLength = 16
            hasSetLength = True

    print("Number of Objects: " + str(numOfObjects))

    # stores the objects  under an object header as a list (each entry is the
    # string representation of the object)
    objs = []

    # reads and stores objects and their prefixes until there are no more
    # objects to read under the given object header
    index = startIndex
    count = 0
    while True:
        # read prefix
        index, prefix = read(index, message, prefixType * 8)
        print("Prefix: " + prefix)

        # find object length for objects without set length based on their prefix
        if not hasSetLength:
            objectLength = int(prefix, 2)

        # read object
        index, object = read(index, message, objectLength)
        print("Object: " + str(object))

        # if the object and prefix are empty, break
        if prefix + object == "":
            objs.append("")
            break

        # otherwise append the prefix and object to the objects list and increment
        # count
        else:
            objs.append(prefix + object)
            count += 1
            # once all of the objects have been added, break
            if count == numOfObjects:
                break

    return (index, objs)
