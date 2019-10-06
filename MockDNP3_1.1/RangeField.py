###
# Class to define range field used in object headers of DNP3 messages
# Davis Arthur, ORNL
# 7/21/2019
###

from BinaryHexConversions import *

class RangeField:

    # Note: leave any unused field as "" (predef) or 0 (first, last, count)
    # first/last — optional field to indicate index of first/last object under object header
    # count - optional field to indicate the # of objects under object header
    # predef — string used to initialize a range field without using count or first/last directly
    def __init__(self, first, last, count, predef):

        # if the string is predefined...
        if len(str(predef)) > 0:
            # range field string representation is as defined
            self.rangefieldStr = predef
            self.length = len(predef)
            # if the range field is of length 8, initialize as count version of range field
            if self.length == 8:
                self.numOfObjects = int(self.rangefieldStr, 2)
            # if the range field is of length 16, initialize as first/last versiin of range field
            elif self.length == 16:
                self.numOfObjects = int(self.rangefieldStr[8:16], 2) \
                    - int(self.rangefieldStr[0:8], 2) + 1
            # tell user that the range field has not been initialized correctly
            else:
                self.numOfObjects = None
                print("Error initializing range field: Predefined string does" \
                    + " match range field types")
        # if the first and last fields are filled but no others...
        elif first > 0 and last > 0 and count == 0 and predef == "":
            # range field string representation is first index in binary followed by last index
            self.rangefieldStr = intToBinStr(first, 8) + intToBinStr(last, 8)
            self.length = len(self.rangefieldStr)
            self.numOfObjects = last - first + 1
        # if the count field is filled but no others...
        elif count > 0 and first == 0 and last == 0 and predef == "":
            self.rangefieldStr = intToBinStr(count, 8)
            self.length = len(self.rangefieldStr)
            self.numOfObjects = count
        # otherwise produce error
        else:
            self.rangefieldStr = ""
            self.length = 0
            # in this case read all objects
            self.numOfObjects = None
            print("Error initializing range field: invalid parameter entries")

    # return binary string representation of range field
    def __str__(self):
        return self.rangefieldStr + ""
