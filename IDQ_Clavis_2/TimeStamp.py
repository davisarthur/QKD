# QKD TimeStamp class
# Davis Arthur
# 7/2/2019
# Class used to store and compare the time stamps of data entries in the
# IDQ log files

class TimeStamp :
    def __init__(self, year, month, day, hour, minute, second) :
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self) :
        output = str(self.year) + "-" + format(int(self.month), "02") + "-" \
            + format(int(self.day), "02") + "-" + format(int(self.hour), "02") \
            + ":" + format(int(self.minute), "02") + ":" \
            + format(int(self.second), "02")
        return output

# Returns the number of seconds between a timestamp and the initial timestamp.
# Currently this method only works if the month of the initial timestamp is 30
# days long.
    def getRelativeSeconds(self, initialDate) :
        relativeMonths = int(self.month) - int(initialDate.month)
        relativeDays = relativeMonths * 30 + int(self.day) - int(initialDate.day)
        relativeHours = int(self.hour) - int(initialDate.hour)
        relativeMin = int(self.minute) - int(initialDate.minute)
        relativeSec = int(self.second) - int(initialDate.second)
        relativeSec += relativeMin * 60 + relativeHours * 3600 + relativeDays \
            * 24 * 3600
        return relativeSec
