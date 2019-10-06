# QKD SKR main method
# Davis Arthur
# 7/2/2019
# reads in SKR data from the QKDSequence log

# reads for SKR data from the beginning of the QKDSequence.log file
def readFromStartSKR() :

    # read the first line
    line = datafile.readline()

    dataEntriesSKR = []

    # variables used to save first timestamp of file in order to calculate the
    # relative time between a given entry and the first entry in the file
    first = True
    firstTimeStamp = None

    # read each line until the end of the file
    while line != "" :

        # split the entry into a timestamp and a message
        entryComps = line.split("INFO")

        # process timestamp of each entry
        timeStampComps = entryComps[0].split()
        calendarComps = timeStampComps[0].split("-")
        year = int(calendarComps[0])
        month = int(calendarComps[1])
        day = int(calendarComps[2])
        timeComps = timeStampComps[1].split(":")
        hour = int(timeComps[0])
        minute = int(timeComps[1])
        second = int(timeComps[2])

        entryTimestamp = TimeStamp(year, month, day, hour, minute, second)

        # save the timestamp of the first entry
        if first :
          firstTimestamp = entryTimestamp
          first = False


        # Not all message types follow the same structure. If the entry
        # components list is only of length 1, it is not SKR data and can be ignored
        if len(entryComps) > 1 :
            # split the message into message type and message title/value
            messageComps = entryComps[1].split(":")

        # if the entry contains secret key rate data, record this entry
        if "Secret Key Rate" in messageComps[1]:
            # splits privacy amplification data into title of value and value
            type = "Secret Key Rate"

            # extract the SKR value from the entry
            titleAndValue = messageComps[1].split("=")
            valueAndUnit = titleAndValue[1].split()
            value = float(valueAndUnit[0])
            entrySKR = DataEntry(entryTimestamp, type, value)
            dataEntriesSKR.append(entrySKR)

        # read next line of data
        line = datafile.readline()

    datafile.close()

    # Create a file to store SKR Data
    SKRfile = open("SKR.txt", "w+")

    for entry in dataEntriesSKR :
          SKRfile.write(str(entry.timestamp.getRelativeSeconds(firstTimestamp)) \
            + "\t" + str(entry.value) + "\n")
          print(str(entry))

    SKRfile.close()

# read from first time stamp of interest
def readFromTimeStampSKR(firstTimeStampIn) :

    # read the first line of QKDSequece.log
    line = datafile.readline()
    print("Reading SKR data from QKDSequence.log file...")

    # list to hold QBER data entries
    dataEntriesSKR = []

    # pass each line in file until program reaches first timestamp of interest
    while line != "" :
        entryComps = line.split("INFO")

        # process timestamp of each entry
        timeStampComps = entryComps[0].split()
        calendarComps = timeStampComps[0].split("-")
        year = int(calendarComps[0])
        month = int(calendarComps[1])
        day = int(calendarComps[2])
        timeComps = timeStampComps[1].split(":")
        hour = int(timeComps[0])
        minute = int(timeComps[1])
        second = int(timeComps[2])

        entryTimestamp = TimeStamp(year, month, day, hour, minute, second)

        if entryTimestamp.__str__() == enteredTimestamp.__str__() :
            break
        line = datafile.readline()

    # read each line until the end of the file
    while line != "" :

        # split the entry into a timestamp and a message
        entryComps = line.split("INFO")

        # process timestamp of each entry
        timeStampComps = entryComps[0].split()
        calendarComps = timeStampComps[0].split("-")
        year = int(calendarComps[0])
        month = int(calendarComps[1])
        day = int(calendarComps[2])
        timeComps = timeStampComps[1].split(":")
        hour = int(timeComps[0])
        minute = int(timeComps[1])
        second = int(timeComps[2])

        entryTimestamp = TimeStamp(year, month, day, hour, minute, second)

        # Not all message types follow the same structure. If the entry
        # components list is only of length 1, it is not SKR data and can be ignored
        if len(entryComps) > 1 :
            # split the message into message type and message title/value
            messageComps = entryComps[1].split(":")

        # make sure that there is more than one component in the message
        if len(messageComps) > 1 :
            # if the entry contains secret key rate data, record this entry
            if "Secret Key Rate" in messageComps[1]:
                # splits privacy amplification data into title of value and value
                type = "Secret Key Rate"

                # extract the SKR value from the entry
                titleAndValue = messageComps[1].split("=")
                valueAndUnit = titleAndValue[1].split()
                value = float(valueAndUnit[0])
                entrySKR = DataEntry(entryTimestamp, type, value)
                dataEntriesSKR.append(entrySKR)

        # read next line of data
        line = datafile.readline()

    datafile.close()

    # Create a file to store SKR Data
    SKRfile = open("SKR.txt", "w+")

    for entry in dataEntriesSKR :
          SKRfile.write(str(entry.timestamp.getRelativeSeconds(enteredTimestamp)) \
            + "\t" + str(entry.value) + "\n")
          print(str(entry))

    SKRfile.close()

# main method
from TimeStamp import TimeStamp
from DataEntry import DataEntry

# program will read from QKDSequence.log file
datafile = open("QKDSequence.log", "r")

# prompt user to choose first timestamp of interest or read from the beginning
# of the file
userInput = input("Would you like to read from the beginning of the " \
    + "QKDSequece.log file? ('y' or 'n'): ")
if userInput == "y" :
    readFromStartSKR()
elif userInput == "n" :

    # prompt user to enter the first timestamp of interest
    output = "Enter the following information regrading the first timestamp " \
        + "of interest..."
    print(output)

    inputYear = input("Year (4 digits please!): ")
    inputMonth = input("Month (Ex. February = 02): ")
    inputDay = input("Day: ")
    inputHour = input("Hour (military time): ")
    inputMinute = input("Minute: ")
    inputSecond = input("Second: ")

    enteredTimestamp = TimeStamp(inputYear, inputMonth, inputDay, inputHour, \
        inputMinute, inputSecond)
    readFromTimeStampSKR(enteredTimestamp)

else :
    print("Invalid Response: ")
