###
# Classes used to define anolog input (group 30) of variation 2
# Davis Arthur
# 7/22/2019
###

from Flag import *
from BinaryHexConversions import *

# parent class for all objects of group 30
class AnalogInput:

    def __init__(self):
        self.group = 30

        # in our demonstration, the object prefix and range specifier of anolog
        # input values are always 0 (see ObjHeader class under application layer)
        # this could be modified to be more flexible in the future.
        self.objpre = 0
        self.rangespec = 0

# class specific to objects of group 30 variation 2
class AnalogInputInt16(AnalogInput):

    # value — anolog value stored in the outstation
    # flag — DNP3 flag used to give additional data on outstation and particular index
    def __init__(self, value, flag = Flag()):
        AnalogInput.__init__(self)
        self.variation = 2
        self.flag = str(flag)
        self.value = intToBinStr(int(value), 16)

    # binary string representation of analog input variation 2
    def __str__(self):
        return self.flag + self.value
