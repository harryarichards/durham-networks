import socket
import time
import os


def wait_for_connection(sock):
    # Repeat this.
    while True:
        # Server side output that the servers waiting for a connection.
        print('SERVER: waiting for connection.')
        # Gets new socket object conn to send and receive data,
        # addr the address bound to the socket on the client side.
        conn, addr = sock.accept()
        # Receive a 4 byte request from the client and decode it.
        request = conn.recv(4).decode()
        # If the request was 'CONN' output the conenction ip and wait for an operation.
        if request == 'CONN':
            print('SERVER: CLIENT connected ip:<' + str(addr) + '>')
            wait_for_operation(conn, sock)
        else:
            # Otherwise output yet to connect, note there is no timeout here.
            print('SERVER: client yet to connect.')


def upload_file(conn):
    # Receive the filename length from the user as 2 bytes (short int) and convert them to an int.
    file_name_length = int.from_bytes(conn.recv(2), byteorder='little')
    # Receive the filename from the user.
    file_name = conn.recv(file_name_length).decode()
    # If the conditions are met.
    if file_name_length > 0 and file_name != '':
        # Send an acknowledgement that the server is ready to receive data.
        conn.send('ACK'.encode())
        try:
            start_time = time.time()
            # Receive the file size as a 32 bit value and convert it to an int.
            file_size = int.from_bytes(conn.recv(4), byteorder='little')
            # Open a file in the server files directory, and write binary to it.
            with open(os.getcwd() + '/SERVER FILES/' + file_name, 'wb') as f:
                num_bytes_received = 0
                # While we have not received as many bytes as the file size is.
                while num_bytes_received < file_size:
                    # Receive up to 1024 bytes.
                    bytes_received = conn.recv(1024)
                    # Increase number of bytes received by the number we just received.
                    num_bytes_received += len(bytes_received)
                    # Write the bytes received to the new file.
                    f.write(bytes_received)
            process_time = time.time() - start_time
            # Send the number of bytes received to the client as a 32 bit value.
            conn.send(num_bytes_received.to_bytes(4, 'little'))
            # Send the time it took to upload to the client.
            conn.send(str(process_time).encode())
            # Output a statement saying how the upload went.
            print('UPLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(
                num_bytes_received) + ' bytes received of ' + str(file_size) + ' bytes.')
        except TypeError:
            # If there was a type error output the upload failed.
            print('UPLOAD FAILED')
    else:
        # If the conditions weren't met let them know the file doesn't exist.
        print('FILE DOES NOT EXIST.')


def list_files(conn):
    # List the files in the server files directory.
    dir_list = [file for file in os.listdir(os.getcwd() + '/SERVER FILES')
                if os.path.isfile(os.getcwd() + '/SERVER FILES' + '/' + file)]
    # Remove hidden files from the list.
    dir_list = [file for file in dir_list if not file.startswith('.')]
    # Send the encoded number of files in the server files directory to the client.
    dir_list_length = len(dir_list)
    conn.send(dir_list_length.to_bytes(4, 'little'))
    # For each file in the server file directory (excluding hidden files).
    for file_name in dir_list:
        # Send the length of the filename as 2 bytes (a short int).
        file_name_length = len(file_name)
        conn.send(file_name_length.to_bytes(2, 'little'))
        # Send the filename,
        conn.send(file_name.encode())
    # State the files have been listed.
    print('FILES LISTED.')


def download_file(conn):
    # Receive the file name length from the user as 2 bytes and convert it to a short int.
    file_name_length = int.from_bytes(conn.recv(2), byteorder='little')
    # Receive the file name.
    file_name = conn.recv(file_name_length).decode()
    # If the file name received corresponds to a file.
    if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file_name):
        start_time = time.time()
        # Get the size of the corresponding file.
        file_size = os.path.getsize(os.getcwd() + '/SERVER FILES/' + file_name)
        # Send the file size as a 32 bit value.
        conn.send(file_size.to_bytes(4, 'little', signed=True))
        # Open the corresponding file and read its binary.
        with open(os.getcwd() + '/SERVER FILES/' + file_name, 'rb') as f:
            bytes_sent = 0
            # Read up to 1024 bytes.
            bytes_to_send = f.read(1024)
            # Send the bytes we read.
            conn.send(bytes_to_send)
            # Increase the number of bytes sent by the amount we just sent.
            bytes_sent += len(bytes_to_send)
            # While there are still bytes to send repeat the above process.
            while bytes_sent < file_size:
                bytes_to_send = f.read(1024)
                conn.send(bytes_to_send)
                bytes_sent += len(bytes_to_send)
        process_time = time.time() - start_time
        # Output a statement evaluating how the download went.
        print('DOWNLOAD COMPLETE in ' + str(round(float(process_time), 2)) + ' seconds, ' + str(
            bytes_sent) + ' bytes received of ' + str(file_size) + ' bytes.')
    else:
        # If there is no corresponding file send a -1 to the client
        # and output that the file doesn't exist.
        conn.send((-1).to_bytes(4, 'little', signed=True))
        print('FILE DOES NOT EXIST.')


def delete_file(conn):
    # Receive the length of the file name of the file the client wishes to delete.
    file_name_length = int.from_bytes(conn.recv(2), byteorder='little')
    # Receive the file name of the file the client wishes to delete.
    file_name = conn.recv(file_name_length).decode()
    # If the file exists.
    if os.path.isfile(os.getcwd() + '/SERVER FILES/' + file_name):
        # Send a 1 confirming its existence to the user.
        conn.send((1).to_bytes(2, 'little', signed=True))
        # Receive confirmation on whether the user wants to delete the file.
        confirm = conn.recv(1024).decode()
        # If they do.
        if confirm.upper() == 'YES':
            try:
                # Try and delete the file and let the user know this happened.
                os.remove(os.getcwd() + '/SERVER FILES/' + file_name)
                conn.send('DELETE SUCCESSFUL.'.encode())
                print('FILE DELETED.')
            except OSError:
                # If the delete couldn't happen, let the user know.
                conn.send('DELETE FAILED.'.encode())
                print('DELETE FAILED.')
        else:
            # If they didn't confirm they wanted to delete, abandon the delete.
            conn.send('DELETE CANCELLED.'.encode())
            print('DELETED CANCELLED.')
    else:
        # If it doesn't exist send a -1 confirming it doesn't exist.
        conn.send((-1).to_bytes(2, 'little', signed=True))
        print('FILE DOES NOT EXIST.')


def wait_for_operation(conn, sock):
    while True:
        # Repeat the below.
        print()
        # Wait to receive a 4 byte operation and decode it when it comes.
        print('SERVER: waiting for an operation from client.')
        operation = conn.recv(4).decode()
        # Below is obvious.
        if operation == 'CONN':
            print('SERVER: CONNECTION ESTABLISHED')
        elif operation == 'UPLD':
            upload_file(conn)
        elif operation == 'LIST':
            list_files(conn)
        elif operation == 'DWLD':
            download_file(conn)
        elif operation == 'DELF':
            delete_file(conn)
        elif operation == 'QUIT':
            # If the operation was quit, excit the while loop and wait for a connection again.
            conn.close()
            return
        else:
            # If the input wasn't one of the above it wasn't valid.
            print('NOT A VALID OPERATION.')


def set_up():
    try:
        while True:
            host = '127.0.0.1'
            port = 9000
            sock = socket.socket()
            # Bind the socket to the address above.
            sock.bind((host, port))
            sock.listen(1)
            # Now we have the server running, wait for a connection from a client.
            wait_for_connection(sock)
    except Exception as e:
        #If the socket was already bound to the above port then we have a socket error.
        sock.close()
        print('SOCKET ERROR.')


if __name__ == '__main__':
    # At the start of the program, call the set up function.
    set_up()