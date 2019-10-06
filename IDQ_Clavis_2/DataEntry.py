# QKD DataEntry Class
# Davis Arthur
# 7/2/2019
# Class used to summarize data entries in the rawlogs file of IDQ system

class DataEntry :
    def __init__(self, timestamp, type, value) :
        self.timestamp = timestamp
        self.type = type      # label of data entry (Ex. QBER)
        self.value = value    # reported measurement

    def __str__(self) :
        output = "Timestamp: " + str(self.timestamp)
        output += "\tType: " + str(self.type) + "\tValue: " + str(self.value)
        return output
