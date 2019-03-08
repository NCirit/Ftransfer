import socket
import _thread as td
import os , hashlib
from tkinter import *
from tkinter import filedialog

class Client:
    def __init__(self):
        self.window = Tk()
        self.Frame = []
        self.Frame.append(Frame(self.window))
        self.Frame.append(Frame(self.window))
        self.Frame.append(Frame(self.window))
        self.Frame.append(Frame(self.Frame[2]))
        self.Frame[0].pack(fill=BOTH)
        self.Frame[2].pack(fill=BOTH)
        self.Frame[1].pack(fill=BOTH)
        
        self.Frame[3].grid(sticky="NSWE")
        self.BUFF = 2**20
        
        self.strHost = StringVar()
        self.strHost.set("Host")
        self.strPort = StringVar()
        self.strPort.set("port")
        # Upload Info
        self.UInfo = StringVar()
        self.UInfo.set("Upload Progress: ")
        # Download Info
        self.DInfo = StringVar()
        self.DInfo.set("Download Info :")
        # MD5
        self.MD5 = StringVar()
        self.MD5.set("MD5")
        # does progress is done
        self.PInfo = StringVar()
        self.PInfo.set("Progress :")

        # Response from server
        self.Response = StringVar()
        self.Response.set("Response :")
        # File Names from server for listbox
        self.FileNames = StringVar()

        # For selecting name from listbox
        self.Selected = False
        
        rd = StringVar()
        rd.set("Ports : 4884 for upload , 4994 for download.")
        
        Label(self.Frame[3],text="Host:").grid(row = 1,column = 0,sticky="S")
        Entry(self.Frame[3],textvariable=self.strHost).grid(row=1,column = 1,sticky="S")

        Label(self.Frame[3],text="Port:").grid(row = 2,column = 0)
        Entry(self.Frame[3],textvariable=self.strPort).grid(row=2,column = 1,sticky="S")

        
        Entry(self.Frame[2],textvariable=rd,state="readonly",width=len(rd.get())).grid()
        
        Button(self.Frame[3],text="Connect",command=self.Connect).grid(row=1,column = 9,rowspan = 2,columnspan=2,sticky="NSWE")
        
        #Upload Download Button
        self.UD = Button(self.Frame[1],text="",command=None,height=2)

        #Upload Frame
        self.UFrame = Frame(self.Frame[1])
        Label(self.UFrame,textvariable=self.MD5).grid(column=3,columnspan=10,sticky="EW")
        Label(self.UFrame,textvariable=self.UInfo).grid(column=3,columnspan=10,sticky="EW")
        Label(self.UFrame,textvariable=self.PInfo).grid(column=3,columnspan=10,sticky="EW")
        Label(self.UFrame,textvariable=self.Response).grid(column=3,columnspan=10,sticky="EW")
        #Download Frame
        self.DFrame = Frame(self.Frame[1])
        Label(self.DFrame,textvariable=self.MD5).grid(row=1,column=1,columnspan=10,sticky="EW")
        Label(self.DFrame,textvariable=self.DInfo).grid(row=2,column=1,columnspan=10,sticky="EW")
        Label(self.DFrame,textvariable=self.PInfo).grid(row=3,column=1,columnspan=10,sticky="EW")
        Label(self.DFrame,textvariable=self.Response).grid(row=4,column=1,columnspan=10,sticky="EW")
        # Scrollbar for listbox
        self.ListFrame = Frame(self.Frame[1])
        scrollbar = Scrollbar(self.ListFrame)
        Button(self.ListFrame,text= 15*" "+"Download Selected File"+" "*15,command=self.GetIndex).grid(row=0,column=1,sticky="EW")
        self.FileList = Listbox(self.ListFrame,yscrollcommand=scrollbar.set,height=10,width=10,listvariable=self.FileNames)
        scrollbar.config(command=self.FileList.yview)
        scrollbar.grid(row=1,column=0,rowspan=10,sticky="NSE")
        self.FileList.grid(row=1,column=1,sticky="NSEW")
       
        

        self.window.mainloop()
    def GetIndex(self):
        if self.FileList.curselection()==():
            self.PInfo.set("Progress : Please get file names first.")
            return
        state = self.FileList.get(self.FileList.curselection())
        index = self.NameList.index(state)
        self.Index = index
        self.Selected = True
    def Connect(self):
        self.Host = self.strHost.get()
        self.Port = self.strPort.get()

        if self.Port == "4884":
            self.Port=int(self.Port)
            self.UD["command"] = self.Upload
            self.UD["text"] = "Upload"
            self.UD.grid(sticky = "EW",column=3)
            self.UFrame.grid(column=3)
            self.DFrame.grid_forget()
            self.ListFrame.grid_forget()
        elif self.Port == "4994":
            self.Port=int(self.Port)
            self.UD["command"] = self.Download
            self.UD["text"]  = "Get File Names"
            self.UD.grid(sticky = "EW",column=3)
            self.DFrame.grid(column=3,columnspan=9,sticky="EW")
            self.UFrame.grid_forget()
            self.ListFrame.grid(row=6,column=1,columnspan=15,sticky="EWNS")
     
    def Upload(self):
        self.Socket = socket.socket()    
        self.Path = filedialog.askopenfilename()
        if self.Path =='':
            return
        try:
            self.Socket.connect((self.Host,self.Port))
        except TimeoutError:
            self.PInfo.set("Timeout Error")
            return
        td.start_new_thread(self.SendData,())

    def Download(self):
        self.Socket = socket.socket()
        self.PInfo.set("Connecting...")
        try:
            self.Socket.connect((self.Host,self.Port))
        except TimeoutError:
            self.PInfo.set("Timeout Error")
            return
        self.PInfo.set("Connected!")
        td.start_new_thread(self.GetData,())

    def GetData(self):
        self.PInfo.set("Info: "+"Receiving file names...")
        info = self.Socket.recv(2048)
        while len(info) ==0:
            info = self.Socket.recv(2048)
        self.PInfo.set("Info: "+"File names received")
        
        info = info.decode("utf-8").split("\n")
        self.NameList = info[:-1]
        self.FileNames.set(tuple(info[:-1]))
        while not self.Selected:
            pass
        self.Socket.send(str(self.Index).encode("utf-8"))
        fileName = info[self.Index]
        self.Response.set(self.Socket.recv(1).decode("utf-8"))

        info = self.Socket.recv(512)
        info = info.decode("utf-8").split("\n")
        hata = False
        try:
            fileSize = int(info[0])
            
            MD5 = info[2]
            BUFF = int(info[3])
        except ValueError:
            self.PInfo.set("Value Error")
            hata = True
        except IndexError:
            self.PInfo.set("Index Error")
            hata = True
        if hata:
            self.Socket.send("0".encode("utf-8"))
            self.Socket.close()
            return
        self.Socket.send("1".encode("utf-8"))
        self.MD5.set("MD5: "+ MD5)
        self.DInfo.set("File Size: "+str(fileSize) +"File Name: "+ fileName)
        if not os.path.isdir("downloads"):
            os.mkdir("downloads")
        path = "downloads/"+ fileName
        fl = open(path,"wb")
        while fl.tell() < fileSize:
            self.PInfo.set(format(fl.tell()*100/fileSize,".2f") + "%")
            data = self.Socket.recv(BUFF)
            if len(data) == 0:
                self.PInfo.set("Error")
                fl.close()
                break
            fl.write(data)
        fl.close()
        MD5 = self.md5(path)
        self.MD5.set(MD5)
        self.Socket.send(MD5.encode("utf-8"))
        self.Response.set("Downloaded File MD5: " + MD5)
        self.PInfo.set("Progress Completed")
        self.Selected = False
        
        
    def md5(self,path=None):
        pt = self.Path if path == None else path
        hash_md5 = hashlib.md5()
        with open(pt, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    def SendData(self):
        self.PInfo.set("Progress started")
        self.Size = (os.stat(self.Path).st_size)
        
        self.MD5.set("MD5 : " + self.md5())
        info = (str(self.Size) + "\n"+ self.Path.split('/')[-1]+"\n"+self.MD5.get()+"\n"+str(self.BUFF)).encode("utf-8")
        size = self.Size//self.BUFF
        self.Socket.send(info)
        
        self.Response.set("Response: "+self.Socket.recv(512).decode("utf-8"))
        
        fl = open(self.Path,"rb")
        for i in range(size + 1):
            d = fl.read(self.BUFF)
            self.UInfo.set("Upload Info: " + format((i+1)*self.BUFF/(1e+6),".2f") + " MB " +format((i+1)*100/(size+1),".2f") +"% Sending...")
            self.Socket.send(d)
        fl.close()
        self.Response.set("MD5 from server: "+self.Socket.recv(32).decode("utf-8"))
        self.PInfo.set("Progress Completed.")

if __name__ == "__main__":
    Client()
