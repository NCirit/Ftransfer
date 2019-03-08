import _thread as td
import RandName
import os , datetime , hashlib
class Client:
    def __init__(self,con,add,request):
        # Request True for Upload, false for Download
        # Connection
        self.Cn = con
        # Connected address
        self.Address = add
        self.Log("")
        # buffer for recv method
        self.BUFF = 2**2
        self.Prog = 0
        self.Date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.Log(self.Address ,"connected at" ,self.Date," Request:","upload" if request else "Download")
        if request:
            #Read File Info
            self.RFI()
        else:
            #Send File Info
            td.start_new_thread(self.SFI,())

    # Send File Info
    def SFI(self):
        self.BUFF = 2**22
        fileNames = os.listdir("uploads/")
        fileNames.sort() 
        msg = ""
        for i in range(len(fileNames)):
            msg += fileNames[i][:-17]+"\n"
        if len(fileNames) == 0:
            msg = "No file"
        self.Cn.send(msg.encode("utf-8"))
        print("names sended.")
        try:
            fileIndex = self.Cn.recv(64)
        except ConnectionResetError:
            self.Cn.close()
            return
        while len(fileIndex) == 0:
            try:
                fileIndex = self.Cn.recv(64)
            except ConnectionResetError:
                self.Cn.close()
                return

        
        hata = False
        try:
            fileIndex = int(fileIndex.decode("utf-8"))
        except ValueError:
            hata = True

        if fileIndex < 0 or fileIndex >= len(fileNames):
            hata = True
        if hata:
            self.Log("File Index Error")
            self.Cn.send("0".encode("utf-8"))
            self.Cn.close()
            return
        self.Cn.send("1".encode("utf-8"))
        path = "uploads/"+fileNames[fileIndex]
        self.Path=path
        fileSize = (os.stat(path).st_size)
        MD5 = self.md5()
        msg = (str(fileSize) +"\n"+ fileNames[fileIndex] +"\n"+MD5+"\n"+str(self.BUFF))
        self.Cn.send(msg.encode("utf-8"))

        prog = self.Cn.recv(64)

        if prog.decode("utf-8") != "1":
            self.Log("File ınformation couldn't send.")
            self.Cn.send("Error".encode("utf-8"))
            self.Cn.close()
            return
        td.start_new_thread(self.StartDownload,(path,fileSize,))
    def StartDownload(self,path,size):
        fl = open(path,"rb")
        size = size//self.BUFF
        self.Log("Progress started.")
        for i in range(size + 1):
            data = fl.read(self.BUFF)
            self.Cn.send(data)
        resp = self.Cn.recv(64)
        print(resp.decode("utf-8"))
        self.Log("Progress Completed.")
        
    # Read File Info
    def RFI(self):
        try:
            info = self.Cn.recv(1024)
        except ConnectionResetError:
            self.Log("Connection closed by :",self.Address)
            return
        info = info.decode("utf-8").split('\n')
        hata = False
        try:
            #File Size
            self.Size = int(info[0])
            self.BUFF = int(info[3])
        except ValueError:
            hata = True
        except IndexError:
            hata = True

        if hata:
            self.Log("Index or Value error")
            self.Cn.send("Error".encode("utf-8"))
            self.Cn.close()
            return
        #File Name
        self.Fname = info[1]

        self.MD5 = info[2]

        self.Cn.send("Information received.".encode("utf-8"))
        td.start_new_thread(self.StartUpload,())
    # Starting upload
    def StartUpload(self):
        # File path for saving
        name = self.Fname.replace("/","")+RandName.RandomName.Create(17)
        self.Path = "uploads/"+ name
        self.Log(self.Address , " uploading :",name,"\tMD5:",self.MD5)
        buffCount = self.Size // self.BUFF
        fl = open(self.Path,"wb")
        i = 0
        while fl.tell() < self.Size:
            try:
                data = self.Cn.recv(self.BUFF)
            except ConnectionResetError:
                self.Log("Connection closed by :",self.Address)
                fl.close()
                return
            fl.write(data)
        fl.close()
        md5p = self.md5()
        self.Log(self.Address , " uploaded :",name,"\tMD5:",md5p)
        self.Cn.send(md5p.encode("utf-8"))

    def Progress(self):
        while self.Prog < 100:
            print(self.Address,": ",format(self.Prog,".2f"),"%")
        print(self.Address,": ",format(self.Prog,".2f"),"%")
        print("Completed.")

    def Log(self,*data):
        msg = ""
        for i in range(len(data)):
            msg += str(data[i])
            msg += " "
        msg += "\n"
        if os.path.exists("logs/logs.txt"):
            fl = open("logs/logs.txt","a")
            fl.write(msg)
        else:
            fl = open("logs/logs.txt","w")
            fl.write(msg)
        fl.close()

    def md5(self):
        hash_md5 = hashlib.md5()
        with open(self.Path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

