import socket
import _thread as td
from client import Client
def Main():
    td.start_new_thread(UploadServer,())
    DownloadService()
def DownloadService():
    host = ""
    port = 4994 
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    sock.bind((host,port)) 
    sock.listen(1)
    userList = []
    NewPrint("Download Service Started")
    while True:
        NewPrint("Waiting for users.")
        con ,addr = sock.accept()
        userList.append(Client(con,addr,False))
    sock.close()

def UploadService():
    host = ""
    port = 4884 
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    sock.bind((host,port)) 
    sock.listen(1)
    userList = []
    NewPrint("Upload Service Started")
    while True:
        NewPrint("Waiting for users.")
        con ,addr = sock.accept()
        userList.append(Client(con,addr,True))
    sock.close()
def NewPrint(data):
    print(".>"+data)
if __name__ == "__main__":
    Main()
