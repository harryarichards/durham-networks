Install Pyro4:
pip install Pyro4

or

download the source distribution archive 
and input the following in terminal/commandprompt:
python setup.py install.

In CLIENT sub-directory:
client.py
Ib SERVER sub-directory:
server.py

Open terminal/commandprompt:
Navigate to server.py
input python3 server.py

Open terminal/commandprompt:
Navigate to client.py
input python3 client.py

server.py must be running for client.py to function.

INPUT CONN to connect
INPUT UPLD to upload a file, any file you wish to upload must be in the same directory as client.py and are uploaded to the SERVER FILES subdirectory in the SERVER sub-directory.
INPUT LIST to list files, lists files in SERVER FILES subdirectory in the SERVER sub-directory.
INPUT DWLD to download a file, any file you wish to download must be in the SERVER FILES subdirectory in the SERVER sub-directory.
INPUT DELF to delete a file, deletes specified file from the SERVER FILES subdirectory in the SERVER directory.
INPUT QUIT to quit the program.

You may quit the client program and re-connect by running client.py again.
There is no timeout on server.py and in order to stop it you must do so manually.