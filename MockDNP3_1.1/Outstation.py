###
# Class for outstation, includes methods required for simulated interchange
# Davis Arthur, ORNL
# 7/22/2019
###

from get_id3100_keys import *
from BinaryHexConversions import *
from HMAC_SHA_256 import *
from ApplicationLayer import *
from RangeField import *
from AuthenticationMessages import *
from AnalogInput import *
from DNP3Reader import *
from Database import *

class Outstation:

    # function codes required for simulated interchange
    READ = 1
    AUTHREQ = 32
    RESPONSE = 129
    AUTHREP = 131

    # database - outstation's database (see Database.py)
    # masterIP - IP address of master station
    # keyFile - file that holds the secret key as binary string
    def __init__(self, database, masterIP = "0.0.0.0", keyfile = "fakeSecretKey.txt"):
        self.database = database
        self.masterIP = masterIP
        self.keys = initial_load(keyfile)[1]
        self.macholder = "" # holds mac value to compare to challenge reply
        self.waitingForAuth = False # true after sending authentication challenge
        self.buffer = None # holds challenged asdu until authentication succeeds

        # field to keep track of which keys from the keys list have been used.
        # with each use of a 256-bit authentication key, increment this field by 1
        self.keyNum = 0

        # fields to hold Master's session and update keys
        self.monitoringSessionKey = ""
        self.controllingSessionKey = ""

        # initialize the update key as the next two keys in keys list (512-bit update key)
        self.updateKey = self.keys[self.keyNum] + self.keys[self.keyNum + 1]
        print("Update key: " + self.updateKey)
        self.keyNum += 4    # increment key number

        self.usernumber = 0

    # method used to send a session key status back to the master
    # masterUserNum - user number of the master station requesting status
    # returns statusFrag - application layer fragment with session key status object
    def sendSessionKeyStatus(self, masterUserNum):
        statusObj = SessionKeyStatus(masterUserNum)
        statusObjs = [[statusObj]]
        statusObjHeader = ObjHeader(statusObj.group, statusObj.variation, statusObj.objpre, \
            statusObj.rangespec, statusObj.rangeField)
        statusObjHeaders = [statusObjHeader]
        statusAppHeader = AppResHeader(Outstation.AUTHREP)
        statusFrag = AppLayerFragment(statusAppHeader, statusObjHeaders, statusObjs)

        return statusFrag

    # method to read session key change message sent from outstation
    def readSessionKeyChange(self, sessionKeyChangeFrag):

        # read in object from object string
        changeObjStr = str(sessionKeyChangeFrag.objs[0][0])
        objPrefix = changeObjStr[0:16]
        keyChangeSqnNum = changeObjStr[16:48]
        userNumber = changeObjStr[48:64]
        encryptedKeyWrapData = changeObjStr[64:]
        keyLength = int(encryptedKeyWrapData[0:16], 2)
        encryptedConSessKey = encryptedKeyWrapData[16: 16 + keyLength]
        encryptedMonSessKey = encryptedKeyWrapData[16 + keyLength: 16 + 2 * keyLength]
        keyStatusFragment = encryptedKeyWrapData[16 + 2 * keyLength:]

        conSessionKey, monSessionKey = decryptKeyWrapData(self.updateKey, \
            encryptedConSessKey, encryptedMonSessKey)

        print("Decrypted control direction session key: " + conSessionKey)
        print("Decrypted monitor direction session key: " + monSessionKey)
        self.controllingSessionKey = conSessionKey
        self.monitoringSessionKey = monSessionKey


    # method used to approve or disaprove authentication reply
    # authObj - authentication reply object in question
    # returns true if mac value of reply is equal to the mac value being held in
    # the outstation
    def authenticate(self, authObj):
        prefix = authObj[0:16]
        sequenceNum = authObj[16:48]
        usernumber = authObj[48:64]
        macvalue = authObj[64:] # mac value begins at 64th char of authentication reply
        print("Master station MAC value: " + macvalue)
        print("Outstation MAC value: " + self.macholder)
        if macvalue == self.macholder:
            return True
        else:
            return False

    # sends an authorization challenge on a given asdu
    # asdu - challenged asdu
    # keyNum - index of the key being used to generate outstation's mac value (macholder)
    # returns the challenge fragment to be sent to the master
    def sendAuthChallenge(self, asdu, key):

        # crete an authentication challenge of asdu
        chalObj = AuthenticationChallenge(str(asdu))

        # create and attach a prefix to the challenge object specifying object's length
        chalObjPrefix = intToBinStr(len(str(chalObj)), 16)
        chalObj.prefix = chalObjPrefix

        # challenge fragment will only containg the single challenge object
        # (this is at least true for my simulation)
        chalObjs = [[chalObj]]

        # change the macholder value to the macvalue calculated based on the challenge
        # data of the outgoing challenge
        self.macholder = challenge(chalObj.challengeData, key)

        # create the challenge application layer fragment
        chalAppHeader = AppResHeader(Outstation.AUTHREP)
        chalObjHeader = ObjHeader(chalObj.group, chalObj.variation, \
            chalObj.objpre, chalObj.rangespec, chalObj.rangeField)
        chalObjHeaders = [chalObjHeader]
        chalFrag = AppLayerFragment(chalAppHeader, chalObjHeaders, chalObjs)

        return chalFrag

    # responds to read command from master
    # first - first index to return to master
    # last - last index to return to master
    # dataCol - data column where indexes are located (1 for analog input)
    # returns resFrag - the read response application layer fragment
    def sendReadRes(self, first, last, dataCol = 1):

        # create an empty array to hold the values to be returned
        values = [0] * (last - first + 1)
        resObjs = [[]]

        # fill an array of response objects
        index = first
        for value in values:
            # get the value for each index, and create analog input object w/value
            value = self.database.getVal(dataCol, index)
            resObj = AnalogInputInt16(value)

            # append new obj to obj list
            resObjs[0].append(resObj)
            index += 1

        # generate read response application layer fragment
        resAppHeader = AppResHeader(Outstation.RESPONSE)
        resRangeField = RangeField(first, last, 0, "")
        resObjHeader = ObjHeader(resObjs[0][0].group, resObjs[0][0].variation, \
            resObjs[0][0].objpre, resObjs[0][0].rangespec, resRangeField)
        resObjHeaders = [resObjHeader]
        resFrag = AppLayerFragment(resAppHeader, resObjHeaders, resObjs)

        return resFrag

    # responds to authentication reply with an error
    # returns errFrag - application layer fragment containing error message
    def sendError(self):

        # create authentication error object with prefix specifying object length
        errObj = AuthenticationError()
        errObjPrefix = intToBinStr(len(str(errObj)), 16)
        errObj.prefix = errObjPrefix

        # store the object in a list of lists
        errObjs = [[errObj]]

        # create the application layer headers
        errAppHeader = AppResHeader(Outstation.AUTHREP)
        errObjHeader = ObjHeader(errObj.group, errObj.variation, errObj.objpre,\
            errObj.rangespec, errObj.rangeField)
        errObjHeaders = [errObjHeader]

        # create the application layer fragement
        errFrag = AppLayerFragment(errAppHeader, errObjHeaders, errObjs)

        return errFrag

    # reads in a DNP3 message sent from the master station
    # masterMess - binary string recieved from master
    # returns 0 if it is necessary to send authentication challenge
    # returns 1 if it is necessary to perform authentication on authentication reply
    # also returns the asdu that was read
    def readDNP3Mess(self, masterMess):

        # read application header from incoming message
        index, readInAppHeader = readAppHeader(masterMess)

        # read in object headers and their objects while there are more headers
        # in the application layer fragment
        count = 0
        readInObjHeaders = []
        readInObjs = []
        while True:

            # read object header
            index, readInObjHeader = readObjHeader(index, masterMess)

            # if there is no object header to read, break from loop
            if readInObjHeader == None:
                break

            # append object header to list of objects
            readInObjHeaders.append(readInObjHeader)

            # read objects under the header and append them to a list
            index, objsOfHeader = readObjs(index, readInObjHeader, masterMess)
            readInObjs.append(objsOfHeader)

            # increment to indicate a new object header
            count += 1

        # creates the read in asdu
        readInAsdu = AppLayerFragment(readInAppHeader, readInObjHeaders, readInObjs)

        print("")

        # if the read in fragment has a READ function code, send authentication challenge
        if readInAppHeader.functionCode == intToBinStr(Outstation.READ, 8):
            print("Requires authentication to process asdu.")
            return (0, readInAsdu)

        # if the read in fragment has an authentication function code, perform authentication
        elif readInAppHeader.functionCode == intToBinStr(Outstation.AUTHREQ, 8):
            if readInAsdu.objHeaders[0].variation == intToBinStr(2, 8) \
                or readInAsdu.objHeaders[0].variation == intToBinStr(7, 8):
                print("Performing Authentication...")
                return (1, readInAsdu)
            elif readInAsdu.objHeaders[0].variation == intToBinStr(4, 8):
                print("Session key status request recieved. Preparing session key status...")
                return (2, readInAsdu)
            elif readInAsdu.objHeaders[0].variation == intToBinStr(6, 8):
                print("Session key change message recieved. Updating session keys...")
                return (3, readInAsdu)

        # otherwise there is an issue
        else:
            print("Error: Function code does not match sample types, or " \
                + "outstation is not waiting for authentication." \
                + " Outstation read function code: " + readInAppHeader.functionCode)

    # takes in the result of readDNP3Mess and performs the necessary action
    # actionTuple - (actionCode, readInAsdu)
        # actionCode - specifies action required by outstation
    # returns outgoingChalFrag - challenge message sent to master
    # returns 0 or 1 - final action code based on whether or not authentication
    # was successful
    def action(self, actionTuple):

        # unpack tuple
        actionCode, asdu = actionTuple

        # if the action code is 0, send authentication challenge on readInAsdu
        if actionCode == 0:

            # create authentication challenge object using read in asdu
            outgoingChalFrag = self.sendAuthChallenge(asdu, self.controllingSessionKey)
            self.waitingForAuth = True  # now the outstation is waiting for reply
            self.buffer = asdu  # place read in asdu in buffer
            return outgoingChalFrag

        # if action code is 1, perform authentication
        elif actionCode == 1:

            # if authentication works then return 0
            if self.authenticate(asdu.objs[0][0]):
                return 0
            # if authentication fails return 1
            else:
                return 1

            self.waitingForAuth = False # no longer waiting for authentication

        # if action code is 2, send session key status
        elif actionCode == 2:

            outgoingSessKeyStatusFrag = self.sendSessionKeyStatus(1)
            return outgoingSessKeyStatusFrag

        elif actionCode == 3:

            self.readSessionKeyChange(asdu)
            return "Session keys initialized."

    # method to perform final action if the master sent an authentication reply
    # finalCode - output from action method
    # returns resFrag - read response fragment if authentication was successful
    # returns errFrag - error fragment if authentication failed
    def finalAction(self, finalCode):
        # if authentication was succesful process/respond to asdu in the buffer
        if finalCode == 0:

            print("Authentication Succeded. Sending read response...")
            asdu = self.buffer
            rangeFieldStr = asdu.objHeaders[0].rangeField.rangefieldStr

            # get the first and last indexes requested in the read request
            first = int(rangeFieldStr[0:8], 2)
            last = int(rangeFieldStr[8:16], 2)

            # generate read response
            resFrag = self.sendReadRes(first, last)
            print("Read Response: " + str(resFrag))

            return resFrag

        # if authentication failed, send default error message
        elif finalCode == 1:
            errFrag = self.sendError()
            print("Authentication Failed. \n" + "Error message: " + str(errFrag))
            return errFrag
