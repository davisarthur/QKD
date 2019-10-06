import socket
import sys
from Master import *

# prompt user to enter secret key file
keyfile = input("Input secret key file: ") #"fakeSecretKey.txt"

# create server socket
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# create master (usernumber 1)
mast = Master(keyfile, 1)
print("")

# bind server to localhost and port 8080, and listen for 1 connection
serv.bind(('0.0.0.0', 8080))
serv.listen(1)

while True:
    # accept connections from outside
    (conn, addr) = serv.accept()
    print("")
    print("Sending a session key status request to outstation...")
    messageOut = str(mast.sendStatusRequest())

    while True:

        # send message to client
        conn.send(messageOut.encode())

        # read data sent from client
        messageIn = conn.recv(2048).decode()
        print("")
        print("Client: " + messageIn)
        print("")

        # if no data is sent, exit the program
        if not messageIn:
            sys.exit()

        # if the outstation has just initialized the session keys, initiate sample interchange
        elif "Session keys initialized." in messageIn:
            print("Sending READ command...")
            messageOut = str(mast.sendSampleRequest())

        # if "Finished." is in one of the outstations method, exit the program
        elif "Finished." in messageIn:
            sys.exit()

        # set message out to the appropriate response to the read in data
        else:
            print("Breaking down client's message...")
            messageOut = str(mast.action(mast.readDNP3Mess(messageIn)))

    conn.close()
    print("client disconnected")
