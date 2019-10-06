###
# Classes associated with Secure Authentication objects (group 120)
# Davis Arthur
# 7/22/2019
###

import secrets
from BinaryHexConversions import *
from HMAC_SHA_256 import *
from RangeField import *
from OneTimePad import *

# parent class for all objects of group 120
class AuthenticationMessage:

    # Challenge sequence number; incremented with each new message
    # Note: sequence number has not been tested and may not work as intended.
    # However, it is not critical to the QKD demonstration
    sequenceNum = 0

    # Initially leave a blank object prefix.
    def __init__(self, prefix = ""):
        self.group = 120
        self.prefix = prefix

# class for authentication challenge messages (group 120 variation 1)
class AuthenticationChallenge(AuthenticationMessage):

    # HMAC-SHA256 for networked connection
    __DEFAUlT_HMAC = 4
    # Reason for challenge is because ASDU is critical
    __DEFAULT_RSN = 1

    # asduStr - challenged asdu
    # usernumber - 0 for an outstation, can be any number for master
    # macalgorithm - code notifying the other party with mac algorithm to use
    # (only HMAC-SHA256 is supported (code number 4))
    # rsn — reason the asdu is challenged
    def __init__(self, asduStr, usernumber = 0, macalgorithnm = __DEFAUlT_HMAC, \
        rsn = __DEFAULT_RSN, prefix = ""):
        AuthenticationMessage.__init__(self, prefix)
        self.variation = 1
        AuthenticationMessage.sequenceNum += 1
        self.sequenceNum = intToBinStr(AuthenticationMessage.sequenceNum, 32)
        self.usernumber = intToBinStr(usernumber, 16)
        self.macalgorithnm = intToBinStr(macalgorithnm, 8)
        self.rsn = intToBinStr(rsn, 8)
        self.challengeData = (str(ChallengeData(asduStr)))
        self.objpre = 5
        self.rangespec = 11
        self.rangeField = RangeField(0, 0, 0, intToBinStr(1, 8))

    # binary string representation of challenge message
    def __str__(self):
        return self.prefix + self.sequenceNum + self.usernumber + self.macalgorithnm \
            + self.challengeData

# class for authentication reply messages
class AuthenticationReply(AuthenticationMessage):

    # challengeDataString - challenge data from challenge message
    # keyString - session key used for authentication
    # usernumber - 0 for an outstation, can be any number for master
    # prefix - indicates length of reply message
    def __init__(self, challengeDataString, keyString, usernumber = 0, \
        prefix = ""):
        AuthenticationMessage.__init__(self, prefix)
        self.variation = 2
        self.sequenceNum = intToBinStr(AuthenticationMessage.sequenceNum, 32)
        self.usernumber = intToBinStr(usernumber, 16)
        self.macvalue = challenge(challengeDataString, keyString) # as binary string
        self.objpre = 5
        self.rangespec = 11
        self.rangeField = RangeField(0, 0, 0, intToBinStr(1, 8))

    # binary string representation
    def __str__(self):
        return self.prefix + self.sequenceNum + self.usernumber + self.macvalue

# class for authentication error messages
# Note: most fields in the message are not developed. However, for the purpose
# of the QKD simulation, it does not matter if the authentication error includes
# time, associationID etc.
class AuthenticationError(AuthenticationMessage):

    # time and authenication id not yet supported
    # later add ptential for key change sequence number instead of challenge sequenceNum
    # errorCode = 1 - authentication failed (only supported code for simulation)
    def __init__(self, associationID = 0, errorCode = 1, time = 0, \
        usernumber = 0, errorText = "", prefix = ""):
        AuthenticationMessage.__init__(self, prefix)
        self.variation = 7
        self.sequenceNum = intToBinStr(AuthenticationMessage.sequenceNum, 32)
        self.usernumber = intToBinStr(usernumber, 16)
        self.associationID = intToBinStr(associationID, 16)
        self.errorCode = intToBinStr(errorCode, 8)
        self.time = intToBinStr(time, 48)
        self.errorText = errorText # default empty
        self.objpre = 5
        self.rangespec = 11
        self.rangeField = RangeField(0, 0, 0, intToBinStr(1, 8))

    # binary string representation
    def __str__(self):
        return self.prefix + self.sequenceNum + self.usernumber \
            + self.associationID + self.errorCode + self.time + self.errorText

# class used to represent challenge data in challenge message
class ChallengeData:

    # asduStr — challenged asdu as a binary string
    def __init__(self, asduStr) :

        self.asduStr = asduStr
        asduLength = len(self.asduStr)

        # Challenge data length will be a multiple of 256. If the challenged ASDU is too
        # long for the challenge data to have 32 random bits, add 256 bits to
        # challenge data.
        counter = 2
        bits = 256
        while (bits - 32) < asduLength :
            bits = counter * 256
            counter += 1

        # Fill the remainder of the challenge data (after challenged asdu) with
        # random bits.
        numRandom = bits - len(self.asduStr)
        self.random = intToBinStr(secrets.randbits(numRandom), numRandom)

    # binary string representation
    def __str__(self) :
        return self.asduStr + self.random

# class for creating key wrap data for session key change messages
class KeyWrapData:

    def __init__(self, controlDirSessionKey, monitorDirSessionKey, keyStatusMessage):

        # all demo keys are 256 bits long
        self.keylength = 256
        self.controlDirSessionKey = controlDirSessionKey
        self.monitorDirSessionKey = monitorDirSessionKey
        self.keyStatusMessage = keyStatusMessage

        # may eventually need this field, but not for current demo
        # used with different key wrap algorithms
        self.paddingData = ""

    # binary string representation
    def __str__(self):
        return intToBinStr(self.keylength, 16) + self.controlDirSessionKey \
            + self.monitorDirSessionKey + str(self.keyStatusMessage) \
            + self.paddingData

# class encrypts the session keys using a one time pad with half of update key and
# each session key. Key length and key status message are not encrypted because
# one time pad is already perfectly secure encryption of session key.
class EncryptedKeyWrapData:

    # updatekey - 512-bit key, each half of the key is used to encrypt a session key
    # keyWrapData - keyWrapData
    def __init__(self, updateKey, keyWrapData):
        self.keylength = 256
        self.encryptedConSessKey = xor(updateKey[0:256], keyWrapData.controlDirSessionKey)
        self.encryptedMonSessKey = xor(updateKey[256:], keyWrapData.monitorDirSessionKey)
        print("Encrypted control direction session key: " + self.encryptedConSessKey)
        print("Encrypted monitor direction session key: " + self.encryptedMonSessKey)
        self.keyStatusMessage = keyWrapData.keyStatusMessage

    # binary string representation
    def __str__(self):
        return intToBinStr(self.keylength, 16) + self.encryptedConSessKey \
            + self.encryptedMonSessKey + str(self.keyStatusMessage)

# function to decrypt session keys from encrypted key wrap data
def decryptKeyWrapData(updateKey, encryptedConKey, encryptedMonKey):

    conSessionKey = xor(updateKey[0:256], encryptedConKey)
    monSessionKey = xor(updateKey[256:], encryptedMonKey)

    return (conSessionKey, monSessionKey)

# class used to create session key status request objects
class SessionKeyStatusRequest(AuthenticationMessage):

    # currently usernumber 1 is the only supported usernumber. This usernumber
    # is used when the user of the master station is anonymous
    # usernumber - usernumber of party making request (0 for outstation, 1 for
    # master)
    def __init__(self, usernumber):
        AuthenticationMessage.__init__(self)
        # object header specifications
        self.objpre = 0
        self.rangspec = 7
        self.rangeField = RangeField(0, 0, 1, "") # range field specifies 1 object
        self.variation = 4

        # user number of requesting party
        self.usernumber = usernumber

    # binary string representation
    def __str__(self):
        return intToBinStr(self.usernumber, 16)

# class used to define session key status objects
class SessionKeyStatus(AuthenticationMessage):

    # session key sequence number. With each new session key, this number
    # should be incremented
    keyChangeSqnNum = 0

    # possible session key statuses for demo
    OK = 1
    NOT_INIT = 2
    AUTH_FAIL = 4

    # hmac algorithm for demo
    __DEFAUlT_HMAC = 4

    # custom key wrap algorithm code
    ONE_TIME_PAD = 129

    # usernumber - user number of requesting party
    # sessionKeyChangeAsdu - most recent session key change request sent
    # keyWrapAlg - algorithm to use when wrapping keys
        # demo only supports AES256 (code 2)
    # keyStatus - status of the two session keys (options above)

    def __init__(self, usernumber, sessionKeyChangeAsdu = "", macvalueStr = "", \
        macalg = 0):

        AuthenticationMessage.__init__(self)

        # key change sequence number is initialized
        SessionKeyStatus.keyChangeSqnNum += 1
        self.keyChangeSqnNum = SessionKeyStatus.keyChangeSqnNum

        # fields for object header
        self.objpre = 5
        self.rangespec = 11
        self.variation = 5
        self.rangeField = RangeField(0, 0, 1, "")

        self.usernumber = usernumber
        self.keyWrapAlg = SessionKeyStatus.ONE_TIME_PAD
        self.keyStatus = SessionKeyStatus.NOT_INIT
        self.macalg = macalg

        # generate challenge data and calculate its length
        self.challengeDataStr = str(ChallengeData(sessionKeyChangeAsdu))
        self.challengeDataLength = len(self.challengeDataStr)

        # if no session key has been initialized, macvalue field should be empty
        # and mac algorithm should be zero.
        # Note: this is the case for this functions use in the demo
        if (self.keyStatus == SessionKeyStatus.NOT_INIT):
            self.macalg = 0
            self.macvalueStr = ""
        else:
            self.macvalueStr = macvalueStr

    # binary string representation
    def __str__(self):

        objString = intToBinStr(self.keyChangeSqnNum, 32) +  intToBinStr(self.usernumber, 16) \
            + intToBinStr(self.keyWrapAlg, 8) + intToBinStr(self.keyStatus, 8) \
            + intToBinStr(self.macalg, 8) + intToBinStr(self.challengeDataLength, 8) \
            + self.challengeDataStr + self.macvalueStr
        prefix = intToBinStr(len(objString), 16)
        self.prefix = prefix

        return self.prefix + objString

# class for session key change objects
class SessionKeyChange(AuthenticationMessage):

    def __init__(self, usernumber, updatekey, controlDirSessionKey, \
        monitorDirSessionKey, keyStatusMessage):

        AuthenticationMessage.__init__(self)

        # object header variables
        self.variation = 6
        self.objpre = 5
        self.rangespec = 11
        self.rangeField = RangeField(0, 0, 1, "")

        self.keyChangeSqnNum = SessionKeyStatus.keyChangeSqnNum
        self.usernumber = usernumber

        self.keyWrapData = KeyWrapData(controlDirSessionKey, monitorDirSessionKey, \
            keyStatusMessage)

        # encrypts the key wrap data using one time pad with update key
        self.encryptedKeyWrapData = EncryptedKeyWrapData(updatekey, self.keyWrapData)

    # binary string representation
    def __str__(self):
        objectString = intToBinStr(self.keyChangeSqnNum, 32) \
        + intToBinStr(self.usernumber, 16) + str(self.encryptedKeyWrapData)
        prefix = intToBinStr(len(objectString), 16)

        return prefix + objectString
