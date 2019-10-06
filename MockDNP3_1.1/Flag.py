###
# Class to define flag used in DNP3 objects.
# Davis Arthur, ORNL
# 7/21/2019
###

class Flag :

    # online - data point is active and accessible
    # restrt - data has not been updated since device was reset
    # commlost - communication error between device with data and the device that requested data
    # remoteforced - data value is overridden in a downstream reporting device
    # localforced - data is overridden by the reporting device
    # overrange - data objects value exceeds valid measurement range of the object
    # ref_err - data value might not have expected level of accuracy
    def __init__(self, online = 1, rstrt = 0, commlost = 0, remoteforced = 0, \
        localforced = 0, overrange = 0, ref_err = 0) :
        self.online = str(online)
        self.restrt = str(rstrt)
        self.commlost = str(commlost)
        self.remoteforced = str(remoteforced)
        self.localforced = str(localforced)
        self.overrange = str(overrange)
        self.ref_err = str(ref_err)
        res = 0  # field reserved for future use
        self.res = str(res)

    # binary string representation of flag 
    def __str__(self) :
        return self.online + self.restrt + self.commlost + self.remoteforced  \
            + self.localforced + self.overrange + self.ref_err +  self.res
