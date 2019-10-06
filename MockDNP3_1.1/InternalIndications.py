###
# Class for internal indication octets used in application layer responses
# Davis Arthur, ORNL
# 7/22/2019
###

# internal indication octets are only included in response messages
class InternalIndications:

    # For the following fields, input a 1 if the condition is true, a 0 if the
    # condition is false

    # br = a broadcast message was received
    # cls1 - cls3 = outstation has unreported class ___ events
    # time = time synchronization is required
    # lclCtrl = 1 or more of outstation's points are in local control mode
    # trbl = abnormal condition of outstation
    # rstrt = outstation restarted
    # nosupport = outstation does not support this function code
    # unkwn = outstation does not support requested operation for objects in request
    # paramerr = parameter error detected
    # evtbuff = even buffer overflow condition exists in outstation
    # exe = the operation requested is already executing
    # configcorr = the outstation detected corrupt configuration
    # res_ = reserved bits for future use
    def __init__(self = 0, br = 0, cls1 = 0, cls2 = 0, cls3 = 0, time = 0, \
        lclCtrl = 0, trbl = 0, restrt = 0, nosupprt = 0, unkwn = 0, \
        paramerr = 0, evtbuff = 0, exe = 0, configcorr = 0, res1 = 0, res2 = 0):
        self.firstOctet = str(br) + str(cls1) + str(cls2) + str(cls3) \
            + str(time) + str(lclCtrl) + str(trbl) + str(restrt)
        self.secondOctet = str(nosupprt) + str(unkwn) + str(paramerr) \
            + str(evtbuff) + str(exe) + str(configcorr) + str(res1) + str(res2)

    # string representation
    def __str__(self):
        return self.firstOctet + self.secondOctet
