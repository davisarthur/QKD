import socket
from Outstation import *

# prompt user to enter secret key file
keyfile = input("Input secret key file: ") # "fakeSecretKey.txt"

# prompt user to enter ip address to connect to
serverIP = input("Input master station IP address: ") #"0.0.0.0"
print("Connecting to " + serverIP)
print("")

# create outstation
db = Database() # database for outstation
db.randomizeCol(1) # randomize the analog input column of database
out = Outstation(db, serverIP, keyfile)
print("")

# print outstation database 4-7 for refference
print("Outstations database before interchange: ")
print("Anolog Input 4: " + str(out.database.getVal(1,4)))
print("Anolog Input 5: " + str(out.database.getVal(1, 5)))
print("Anolog Input 6: " + str(out.database.getVal(1, 6)))
print("Analog Input 7: " + str(out.database.getVal(1, 7)))

# create client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to server via port number 8080
client.connect((serverIP, 8080))

messageOut = "Connected to client"

while True:

    # accept the server's message
    messageIn = client.recv(2048).decode()
    print("")
    print("Server: " + messageIn)
    print("")

    # if the message contains "Finished." break from loop to finish program
    if "Finished." in messageIn:
        # send "Finished." to master to make sure master also exits program
        client.send("Finished.".encode())
        break

    print("Breaking down server's message...")
    actionOutput = out.action(out.readDNP3Mess(messageIn))
    messageOut = None

    # if the action method returns an integer, preform final action
    if isinstance(actionOutput, int):
        messageOut = str(out.finalAction(actionOutput))
    # if the action method resturns an asdu, send the asdu
    else:
        messageOut = str(actionOutput)

    # send a message to the server once connected
    client.send(messageOut.encode())

client.close()
