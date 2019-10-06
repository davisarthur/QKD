###
# Classes used to create headers and fragments of the application layer
# Davis Arthur, ORNL
# 7/22/2019
###

from InternalIndications import *
from BinaryHexConversions import *

# class for application layer fragments
class AppLayerFragment:

    # appHeader - application header of fragment
    # objHeaders - list of object headers in fragment
    # objs - list of a list of objects in fragments (each list corresponds to
    # a specific object header)
    def __init__(self, appHeader, objHeaders, objs):
        self.appHeader = appHeader
        self.objHeaders = objHeaders
        self.objs = objs

    # binary string representation
    def __str__(self):
        output = str(self.appHeader)
        count = 0
        for objheader in self.objHeaders:
            output += str(objheader)
            for obj in self.objs[count]:
                output += str(obj)
            count += 1
        return output

# this class is used to create application fragment request (master to
# outstation) headers
class AppHeader:

    # fir/fin — 1 if it is the first or last fragment in a message
    # con — 1 if receiver should return application confirmation message
    # uns — 1 if message contains unsolicited response or confirms unsolicited response
    # seq — 4 bits to make sure fragments are read in the correct order
    # funct — 1 octet to specify the function code used (1-128)
    def __init__(self, funct, fir = 1, fin = 1, con = 0, uns = 0, seq = 1):
        self.applicationControl = str(fir) + str(fin) + str(con) + str(uns) \
            + intToBinStr(seq, 4)
        self.functionCode = intToBinStr(funct, 8)

    # binary string representation
    def __str__(self):
        return self.applicationControl + self.functionCode

# this class is used for application fragment response (outstation to master) headers
class AppResHeader(AppHeader):

    # ii - internal indications field
    def __init__(self, funct, fir = 0, fin = 0, con = 0, uns = 0, seq = 0, ii = InternalIndications()):
        AppHeader.__init__(self, funct, fir, fin, con, uns, seq)
        self.ii = str(ii)

    # binary string representation
    def __str__(self):
        return AppHeader.__str__(self) + self.ii

# class for object headers in application fragments
class ObjHeader:

    # objpre codes are in hex (3 bit field)
    # objpre = 0 — objects are packed w/o prefix
    # objpre = 1 — objects are prefixed w/one-octet index
    # objpre = 2 — objects are prefixed w/two-octet index
    # objpre = 3 — objects are prefixed w/four-octet index
    # objpre = 4 — objects are prefixed w/one-octet object size
    # objpre = 5 — objects are prefixed w/two-octet object size
    # objpre = 6 — objects are prefixed w/four-octet object size
    # objpre = 7 — reserved for future use

    # rangespec indicates whether a range field is used and if so how large it is.
    # rangespec codes are in hex (4 bit field)
    # rangespec = 0 — 1 octet start and stop indexes — size of range field = 2
    # rangespec = 1 — 2 octet start and stop indexes — size of range field = 4
    # rangespec = 2 - 4 octed start and stop indexes — size of range field = 8
    # rangespec = 3 — 1 octet virtual addresses — size of range field = 2
    # rangespec = 4 — 2 octet virtual addresses — size of range field = 4
    # rangespec = 5 — 4 octet virtual addresses — size of range field = 8
    # rangespec = 6 — no range field — size of range field = 0 (master wants entire group)
    # rangespec = 7 — 1 octet count of objects — size of range field = 1
    # rangespec = 8 — 2 octet count of objects — size of range field = 2
    # rangespec = 9 — 4 octet count of objects — size of range field = 4
    # rangespec = A — reserved for future use
    # rangespec = B — variable format qualifier
        # range field contains 1-octet count of objs — size of range field = 1
    # rangespec = C — reserved for future use
    # rangespec = D — reserved for future use
    # rangespec = E — reserved for future use
    # rangespec = F — reserved for future use

    # res is a one bit field reserved for future use
    def __init__(self, group, variation, objpre, rangespec, rangeField,  res = 0):
        self.group = intToBinStr(group, 8) # 1 octet
        self.variation = intToBinStr(variation, 8) # 1 octet
        self.objpre = intToBinStr(objpre, 3)
        self.rangespec = intToBinStr(rangespec, 4)
        self.qualifierField = str(res) + self.objpre + self.rangespec # 1 octet
        self.rangeField = rangeField

    # binary string representation
    def __str__(self):
        return self.group + self.variation + self.qualifierField \
            + str(self.rangeField)
