###
# Class for DNP3 master with functions to produce simualated interchange
# Davis Arthur, ORNL
# 7/22/2019
###

from get_id3100_keys import *
from BinaryHexConversions import *
from HMAC_SHA_256 import *
from ApplicationLayer import *
from AuthenticationMessages import *
from RangeField import *
from AnalogInput import *
from DNP3Reader import *
from Database import *

class Master:

    # required function codes for simulation
    READ = 1
    RESPONSE = 129
    AUTHREQ = 32
    AUTHREP = 131

    # keyfile - file that contains secret key
    def __init__(self, keyfile, usernumber = 1):
        self.keys = initial_load(keyfile)[1]
        self.outDatabase = Database() # initially a blank database

        # field to keep track of which keys from the keys list have been used.
        # with each use of a 256-bit authentication key, increment this field by 1
        self.keyNum = 0

        # fields to hold Master's session and update keys
        self.controllingSessionKey = ""
        self.monitoringSessionKey = ""

        # initialize the update key as the next two keys in keys list (512-bit update key)
        self.updateKey = self.keys[self.keyNum] + self.keys[self.keyNum + 1]
        print("Update Key: " + self.updateKey)

        self.keyNum += 4    # increment key number

        # usernumber is 1 by default; this signifies anonymous user
        self.usernumber = usernumber

        # print analog inputs index 4-7 for comparison in the simulation
        print("")
        print("Master's version of outstation's database before interchange: ")
        print("Anolog Input 4: " + str(self.outDatabase.getVal(1,4)))
        print("Anolog Input 5: " + str(self.outDatabase.getVal(1, 5)))
        print("Anolog Input 6: " + str(self.outDatabase.getVal(1, 6)))
        print("Analog Input 7: " + str(self.outDatabase.getVal(1, 7)))

    # method to send a session key status request
    # returns requestFrag - application layer fragment with a session key request object
    def sendStatusRequest(self):
        requestObj = SessionKeyStatusRequest(self.usernumber)
        requestObjs = [[requestObj]]
        requestObjHeader = ObjHeader(requestObj.group, requestObj.variation, \
            requestObj.objpre, requestObj.rangspec, requestObj.rangeField)
        requestObjHeaders = [requestObjHeader]
        requestAppHeader = AppHeader(Master.AUTHREQ)
        requestFrag = AppLayerFragment(requestAppHeader, requestObjHeaders, requestObjs)
        return requestFrag

    # method to send a session key change message to the outstation
    # keyStatusFrag - last key status message sent by outstation
    # returns changeFrag - application layer fragment with session key change object
    def sendSessionKeyChange(self, keyStatusFrag):

        # set the session keys
        self.controllingSessionKey = self.keys[self.keyNum + 2]
        self.monitoringSessionKey = self.keys[self.keyNum + 3]

        changeObj = SessionKeyChange(self.usernumber, self.updateKey,
            self.controllingSessionKey, self.monitoringSessionKey, \
            keyStatusFrag)
        changeObjs = [[changeObj]]
        changeObjHeader = ObjHeader(changeObj.group, changeObj.variation,
            changeObj.objpre, changeObj.rangespec, changeObj.rangeField)
        changeObjHeaders = [changeObjHeader]
        changeAppHeader = AppHeader(Master.AUTHREQ)
        changeFrag = AppLayerFragment(changeAppHeader, changeObjHeaders, changeObjs)

        # update the update key
        self.keyNum += 4
        self.updateKey = self.keys[self.keyNum] + self.keys[self.keyNum + 1]

        return changeFrag

    # outstationMess - binary message from outstation
    # returns actionCode and readInAsdu
        # actionCode - indicates what the master should do after reading message
        # (input to action method)
    def readDNP3Mess(self, outstationMess):
        # read application response header from incoming message
        index, readInAppResHeader = readAppResHeader(outstationMess)

        # while there are still object headers in the message, read in object
        # headers and there objects
        count = 0
        readInObjHeaders = []
        readInObjs = []
        while True:

            # read in object header
            index, readInObjHeader = readObjHeader(index, outstationMess)

            # if there are no object headers, break from the loop
            if readInObjHeader == None:
                break

            # append header to header list
            readInObjHeaders.append(readInObjHeader)

            # read in objects under the object header
            index, objsOfHeader = readObjs(index, readInObjHeader, outstationMess)

            # store objects as a list of binary strings in a list containing
            # objects of different headers
            readInObjs.append(objsOfHeader)

            count += 1

        print("")
        # creates the read in asdu
        readInAsdu = AppLayerFragment(readInAppResHeader, readInObjHeaders, readInObjs)

        # if the action code is a response to read command...
        if readInAppResHeader.functionCode == intToBinStr(Master.RESPONSE, 8):
            # send authentication
            print("Reading in requested data...")
            return (0, readInAsdu)

        # if authentication function code is a response to authentication reply...
        elif readInAppResHeader.functionCode == intToBinStr(Master.AUTHREP, 8):
            # if authentication reply is a challenge or error message...
            if readInAsdu.objHeaders[0].variation == intToBinStr(1, 8) \
                or readInAsdu.objHeaders[0].variation == intToBinStr(7, 8):
                print("Authentication challenge recieved. Preparing reply...")
                # perform authentication
                return (1, readInAsdu)

            # if authentication reply is a session key status message...
            elif readInAsdu.objHeaders[0].variation == intToBinStr(5, 8):
                print("Recieved a session key status message. Generating session "\
                    + "key change message...")
                return (2, readInAsdu)

        # otherwise print error message
        else:
            print("Error: Function code does not match sample types, or " \
                + "outstation is not waiting for authentication." \
                + "You entered: " + readInAppHeader.functionCode)

    # returns sampleReqFrag - READ request used to initiate interchange
    def sendSampleRequest(self):

        # Read analog inputs 4-7
        first = 4
        last = 7
        sampleReqAppHead = AppHeader(Master.READ)
        # group 30, variation 2, no prefix, 1 octet start/stop indexes
        sampleReqObjHead = ObjHeader(30, 2, 0, 0, RangeField(first, last, 0, ""))
        # fragment only needs one object header
        sampleReqObjHeads = [sampleReqObjHead]
        # no outgoing objects in request read fragment
        sampleReqObj = ""
        sampleReqObjs = [sampleReqObj]
        # create fragment
        sampleReqFrag = AppLayerFragment(sampleReqAppHead, sampleReqObjHeads, sampleReqObjs)

        return sampleReqFrag

    # asdu - application challenge fragment or error fragment sent by outstation
    # keyNum - key number to use when creating reply
    # returns replyFrag - challenge reply application layer fragment to send to outstation
    def sendChallengeReply(self, asdu, key):

        # if the read in asdu is an authentication error return...
        if asdu.objHeaders[0].variation == intToBinStr(7, 8):
            return "Error message recieved. Finished."

        # the code below is unnecessary, but useful for debugging
        readInChallengeObj = asdu.objs[0][0]
        prefix = readInChallengeObj[0:16]
        sequenceNum = readInChallengeObj[16:48]
        userNum = readInChallengeObj[48:64]
        macalg = readInChallengeObj[64:72]
        rsn = readInChallengeObj[72:80]

        # challenge data begins at index 72 of challenge object
        # why is this not 80?
        challengeData = readInChallengeObj[72:]

        # create challenge reply object with prefix
        replyObj = AuthenticationReply(challengeData, key)
        replyObjPrefix = intToBinStr(len(str(replyObj)), 16)
        replyObj.prefix = replyObjPrefix

        # create object header and application header
        replyAppHeader = AppHeader(Master.AUTHREQ)
        replyRangeField = RangeField(0, 0, 0, intToBinStr(1, 8))
        replyObjHeader = ObjHeader(replyObj.group, replyObj.variation, \
            replyObj.objpre, replyObj.rangespec, replyRangeField)
        replyObjHeaders = [replyObjHeader]
        replyObjs = [[replyObj]]

        # create challenge reply application layer fragment
        replyFrag = AppLayerFragment(replyAppHeader, replyObjHeaders, replyObjs)
        print("Sending authentication reply: " + str(replyFrag))

        return replyFrag

    # actionTuple - result of readDNP3Mess
        # actionCode - indicates action for the master to take
        # readInAsdu
    # returns challenge reply asdu if actionCode = 1
    # returns "Finished." if actionCOde = 0
    def action(self, actionTuple):
        actionCode, asdu = actionTuple

        if actionCode == 0:
            return self.processReadResponse(asdu)

        elif actionCode == 1:
            return self.sendChallengeReply(asdu, self.controllingSessionKey)

        elif actionCode == 2:
            return self.sendSessionKeyChange(asdu)

        else:
            return "Error."

    # asdu - read in READ response asdu
    # return "Finished."
    def processReadResponse(self, asdu):

        # use range field to find the number of inputs to read in as well as the
        # index of the first input
        rangeFieldStr = asdu.objHeaders[0].rangeField.rangefieldStr
        firstValueIndex = int(rangeFieldStr[0:8], 2)

        objs0 = asdu.objs[0] # list of objects under the first object header
        index = firstValueIndex

        # set each read in value in the master's database
        for obj in objs0:
            value = int(obj[8:], 2)
            self.outDatabase.setVal(1, index, value)
            index += 1

        # print the new database entries for debugging
        print("Database has been updated.")
        print("Anolog Input 4: " + str(self.outDatabase.getVal(1,4)))
        print("Anolog Input 5: " + str(self.outDatabase.getVal(1, 5)))
        print("Anolog Input 6: " + str(self.outDatabase.getVal(1, 6)))
        print("Analog Input 7: " + str(self.outDatabase.getVal(1, 7)))

        return "Finished."
