# QKD QBER main method
# Davis Arthur
# 7/2/2019
# Reads each data entry from the rawlogs file and prints data from entries
# that specify QBER

from DataEntry import DataEntry
from TimeStamp import TimeStamp

# program will read from rawlogs file
datafile = open("rawlogs.txt", "r")

# prompt user to enter the first timestamp of interest
output = "Enter the following information regrading the first timestamp of " \
    + "interest..."
print(output)

inputYear = input("Year (4 digits please!): ")
inputMonth = input("Month (Ex. February = 02): ")
inputDay = input("Day: ")
inputHour = input("Hour (military time): ")
inputMinute = input("Minute: ")
inputSecond = input("Second: ")

firstTimestamp = TimeStamp(inputYear, inputMonth, inputDay, inputHour, \
    inputMinute, inputSecond)

# read the first line of rawlogs
line = datafile.readline()
print("Reading QBER data from rawlogs file...")

# list to hold QBER data entries
dataEntries = []

# pass each line in rawlogs until program reaches first timestamp of interest
while line != "" :
    dataEntryComps = line.split()
    dataTimestamp = dataEntryComps[0]
    if dataTimestamp.__str__() == firstTimestamp.__str__() :
        break
    line = datafile.readline()

# process each data entry following first timestamp of interest
while line != "" :
    dataEntryComps = line.split()
    dataTimestampString = dataEntryComps[0]

    # extract timestamp data from each line
    calendarComps = dataTimestampString.split("-")
    year = int(calendarComps[0])
    month = int(calendarComps[1])
    day = int(calendarComps[2])
    timeComps = calendarComps[3].split(":")
    hour = int(timeComps[0])
    minute = int(timeComps[1])
    second = int(timeComps[2])
    entryTimestamp = TimeStamp(year, month, day, hour, minute, second)

    # extract type and value of data entry
    type = dataEntryComps[5]
    value = dataEntryComps[6]

    # add data entry to an array of all data entries following initial timestamp
    dataEntry = DataEntry(entryTimestamp, type, value)
    dataEntries.append(dataEntry)

    # read next line of rawlogs
    line = datafile.readline()

datafile.close()

# create a file with the QBER readings and the time of their measurement
QBERFile = open("QBER.txt", "w+")

# If the data entry is a QBER entry, record its time and value in
# corresponding files. Also, print the string rep of QBER data entry
# for debugging
for entry in dataEntries :
    if entry.type == "QBER" :
        QBERFile.write(str(entry.timestamp.getRelativeSeconds(firstTimestamp)) \
            + "\t" + str(entry.value) + "\n")
        print(str(entry))

QBERFile.close()
