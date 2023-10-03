import socket
import time
import os


def connect():
    try:

        host = '127.0.0.1'
        port = 9000
        sock = socket.socket()
        # Initiates a TCP server connection with the server binded to the host/port.
        sock.connect((host, port))
        # Lets the server know the connection has been initiated.
        sock.send('CONN'.encode())
        # Returns the socket that uses the connection.
        return sock
    except socket.error:
        # If there was a socket error the user is informed of this.
        print('SOCKET ERROR.')
    except:
        # If there was a general error the user is informed the connection did not take place.
        print('Could not connect to server.')


def upload_file(sock):
    # User inputs the file name of the file the user wishes to upload to the server.
    file_name = input('Input the name of the file you wish to upload: ').encode()
    # File name length is the length of the file in bytes.
    # It is 2 bytes as the length will always be a short int.
    file_name_length = len(file_name).to_bytes(2, 'little')
    #If the file exists.
    if os.path.isfile(file_name):
        # We send the file name length followed by the file name.
        sock.send(file_name_length)
        sock.send(file_name)
        # We received a 3 byte string acknowledgement from the server and decode it.
        acknowledgment = sock.recv(3).decode()
        # If the acknowledgement is 'ACK' we know the server is ready to receive data.
        if acknowledgment == 'ACK':
            # We get the file size of the file we're uploading.
            file_size = os.path.getsize(file_name)
            # We send the file size as 4 bytes as we know it is a 32 bit value.
            sock.send(file_size.to_bytes(4, 'little'))
            bytes_sent = 0
            # Open the file we're oploading and read its binary.
            with open(file_name, 'rb') as f:
                # Read the first 1024 bytes (up to 1024), if there is less than this
                # we only read up to 1024.
                bytes_to_send = f.read(1024)
                # Send the first bytes we read.
                sock.send(bytes_to_send)
                # Increase the number of bytes sent by the number of bytes we just sent.
                bytes_sent += len(bytes_to_send)
                # Let the user know what % of the upload we have completed.
                print('UPLOAD ' + str(round(bytes_sent * 100 / file_size, 2)) + '% COMPLETE')
                # If there are still bytes to send we repeat the above process.
                while bytes_sent < file_size:
                    bytes_to_send = f.read(1024)
                    sock.send(bytes_to_send)
                    bytes_sent += len(bytes_to_send)
                    print('UPLOAD ' + str(round(bytes_sent * 100 / file_size, 2)) + '% COMPLETE')
            # Receive the number of bytes sent, converting it from 4 bytes to an integer.
            # (again this value should be up to 32 bits in length).
            bytes_sent = int.from_bytes(sock.recv(4), byteorder='little')
            # Receive the process time.
            process_time = sock.recv(1024).decode()
            # Print a string for the user letting them know how the upload went.
            print('UPLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(
                bytes_sent) + ' bytes transferred of ' + str(file_size) + ' bytes.')
        else:
            # If the server didn't send 'ACK' as an acknowledgement, let the user know.
            print('The server is not ready to receive data.')
    else:
        # If the file doesn't exist, send its filename as a blank string and file size as 0.
        sock.send((0).to_bytes(2, 'little'))
        sock.send(''.encode())
        # Let the user know the filename wasn't valid.
        print('The filename provided is not a valid file.')


def list_directory_contents(sock):
    # Receive the number of files in the server directory.
    dir_size = int.from_bytes(sock.recv(4), 'little')
    dir_list = []
    # Repeat the following for each file in the server directory.
    for i in range(dir_size):
        # Receive the size of the file name of the incoming file (again received as
        # a 2 bytes as its a short int and converted to an int.
        file_name_size = int.from_bytes(sock.recv(2), 'little')
        # Receive the file name and decode it.
        file_name = sock.recv(file_name_size).decode()
        # Add this file name to a list.
        dir_list.append(file_name)
    # Present the contents of the server directory to the user.
    print()
    print('SERVER DIRECTORY CONTAINS: ')
    print()
    for filename in dir_list:
        print(filename)


def download_file(sock):
    # Receive the name of the file the user wishes to download from the server.
    file_name = input('Input the name of the file you wish to download: ')
    # Get the length of the file name and and send it as a short int in binary form (2 bytes).
    file_name_length = len(file_name)
    sock.send(file_name_length.to_bytes(2, 'little'))
    # Send the encoded file name.
    sock.send(file_name.encode())
    # Receive 32 bits as the file size and convert this to an integer.
    file_size = int.from_bytes(sock.recv(4), 'little', signed=True)
    # If the file exists.
    if file_size != -1:
        start_time = time.time()
        # Open a file and write binary to it.
        with open(file_name, 'wb') as downloaded_file:
            num_bytes_received = 0
            # While we have received less bytes than the size of the file.
            while num_bytes_received < file_size:
                # Receive up to 1024 bytes.
                bytes_received = sock.recv(1024)
                # Increase the number of bytes received by the number of bytes we received.
                num_bytes_received += len(bytes_received)
                # Write the bytes we received to the binary file we opened.
                downloaded_file.write(bytes_received)
                # Let the user know what % of the download we have completed.
                print('DOWNLOAD ' + str(round(num_bytes_received * 100 / file_size, 2)) + '% COMPLETE')
        process_time = time.time() - start_time
        # Print a string for the user letting them know how the download went.
        print('DOWNLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(
            num_bytes_received) + ' bytes received of ' + str(file_size) + ' bytes.')
    else:
        # If the file did not exist, let the user know.
        print('FILE STATED DOES NOT EXIST.')


def delete_file(sock):
    # Receive the name of the file the user wishes to delete from the server and encode it.
    file_name = input('Input the name of the file you wish to delete: ').encode()
    # Set the file name size to the length of the file name represented as 2 bytes
    # (as it's a short int).
    file_name_length = len(file_name).to_bytes(2, 'little')
    # Send the length of the file name.
    sock.send(file_name_length)
    # Send the file name.
    sock.send(file_name)
    # Receive 2 bytes from the server and convert them to an int (short int).
    confirm = int.from_bytes(sock.recv(2), byteorder='little', signed=True)
    # If the int received is -1 let the user know the file does not exist.
    if confirm == -1:
        print('FILE DOES NOT EXIST.')
    elif confirm == 1:
        # If the file exists ask the user to confirm they wish to delete the file.
        confirm = input('Please confirm you wish to delete the file, input Yes to delete, input No to cancel.')
        # If the user inputs 'yes' in any case combination.
        if confirm.upper() == 'YES':
            # Send the confirmation from the user.
            sock.send(confirm.encode())
            # Output a message from the server explaining how the delete went.
            print('SERVER MESSAGE: ' + sock.recv(1024).decode())
        # If the user inputs 'no' in any case combination.
        elif confirm.upper() == 'NO':
            # Send the confirmation to the user.
            sock.send(confirm.encode())
            # Let the user know the delete was abandoned.
            print('Delete abandoned by the user!')
            # Output a message from the server explaining the delete was abandoned.
            print('SERVER MESSAGE: ' + sock.recv(1024).decode())
        else:
            # If the user did not input the Yes/No send 'No' as confirmation to the user
            # to not delete the file.
            sock.send('No'.encode())
            # Output then input was not valid so the user abandoned the delete.
            print('Input not valid: Delete abandoned by the user!')
            # Ouput a message similarly from the server.
            print('SERVER MESSAGE: ' + sock.recv(1024).decode())
    else:
        # If the confirm was neither 1 or -1 output that there has been a server error.
        print('SERVER ERROR.')


def quit(sock):
    # Send quit to the server.
    sock.send('QUIT'.encode())
    #Close the socket
    sock.close()
    # Output that the quit has been executed and the session is closed.
    print('QUIT EXECUTED: SESSION CLOSED.')
    exit()



def prompt(sock):
    #Repeat this forever.
    while True:
        #Print a blank line.
        print()
        try:
            try:
                # Try  and get the operation the user wishes to perform from the user.
                operation = input('Input the operation you wish to perform (CONN, UPLD, LIST, DWLD, DELF, QUIT): ')
            except:
                # This exception seems strange but it deals with the event that the user
                # closes terminal manually before inputting 'QUIT'.
                # This causes a signal hang-up which the exception deals with rather than the
                # server entering a loop.
                quit(sock)
            # If the length of the operation is 4.
            if len(operation) == 4:
                if operation == 'CONN':
                    if sock == None:
                        # If the socket is none, initiate a TCP connection and return it as socket.
                        sock = connect()
                        # Now if the socket is not none (it may still be if the server
                        # wasn't running).
                        if sock != None:
                            # Send the connect operation to the user.
                            sock.send('CONN'.encode())
                        else:
                            # If the server wasn't running let the user know.
                            print('Server not yet running.')
                    else:
                        # If the socket wasn't none let the user know the connection is already
                        # established.
                        print('CONNECTION ALREADY ESTABLISHED.')
                # If the operation inputting is not CONN or QUIT or a blank string.
                if operation != '' and operation != 'CONN' and operation != 'QUIT':
                    try:
                        # If the socket is not none.
                        if sock != None:
                            # Use the TCP connection to send the operation to the server.
                            sock.send(operation.encode())
                        else:
                            # Otherwise let the user know how to initialise a connection.
                            print('Initialise a connection before inputting operations.')
                            print('Input CONN to initialise a connection.')
                    except socket.error:
                        # If there was a socket error let the user know and prompt them to re-input.
                        print('SOCKET ERROR.')
                        prompt()
                # If the socket connection has been initialised.
                if sock != None:
                    # The below is pretty obvious.
                    if operation == 'UPLD':
                        upload_file(sock)
                    elif operation == 'LIST':
                        list_directory_contents(sock)
                    elif operation == 'DWLD':
                        download_file(sock)
                    elif operation == 'DELF':
                        delete_file(sock)
                    elif operation == 'QUIT':
                        quit(sock)
                    elif operation != 'CONN':
                        # If the operation wasn't one of those stated then let the user know it
                        # wasn't valid and prompt them to re-input.
                        print('The operation you inputted is not valid.')
            else:
                # If the length of the operation is not 4 output that the operation
                # is not valid as all valid operations are 4 letters..
                print('The operation you inputted is not valid.')
        except KeyboardInterrupt:
            # If the client program was stopped from running perform the quit function.
            quit(sock)

if __name__ == '__main__':
    #At the start of the program, intialise the socket and perform the prompt operation with it.
    sock = None
    prompt(sock)