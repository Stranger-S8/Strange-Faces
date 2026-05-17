import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from PIL import Image
import cv2
import threading
import database as db
from tkinter import messagebox,filedialog
from drive import DriveUpload
# from Detection import DetectFace
import time
from datetime import datetime
from fpdf import FPDF
import os 

class Task:
    def __init__(self):
        self.obj=DriveUpload()
        self.obj1=db.Admin()
        self.db=db.Database()
        
    def back(self,*args):
        for i in args:
            i.destroy()
    
    def uploadImage(self,label,btn,infoLabel,regBtn,AridNo):
            image_path=filedialog.askopenfilename(filetypes=[("Image Files","*.jpg;*.jpeg;*.png")])
            if image_path:
                infoLabel.configure(text="Please Wait We Are Processing Your Image")
                img=ctk.CTkImage(light_image=(Image.open(image_path)),size=(150,150))
                btn.place_forget()
                regBtn.configure(state="normal")
                label.configure(image=img)
                a = self.obj.uploadPhoto(image_path,AridNo)
                if a:
                    infoLabel.configure(text="Image Processed and Stored Successfully")
                else:
                    infoLabel.configure(text="Failed To Upload ")

    
    def ProcessImage(self,label,btn,infoLabel,regBtn,AridNo):
         if AridNo=="":
            messagebox.showerror("Error","Please Fill the Form First")
         else:
             self.thread_upload=threading.Thread(target=self.uploadImage,args=(label,btn,infoLabel,regBtn,AridNo))
             self.thread_upload.start()
    
    def Reset(self):
    
        if os.path.exists("EncodedFile.p"):
            result = messagebox.askyesno("Delete All Dataset","Do You Want To Proceed")
            if result:
                self.obj1.ClearAll(self.db)
                os.remove("EncodedFile.p")
                messagebox.showinfo("Sucess","Operation Sucessfull")
            else:
                messagebox.showerror("Aborted","Operation Aborted")
        else:
            messagebox.showerror("Error","Resources Missing")
        
class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db=db.Database()
        self.obj1=db.Admin()
        self.obj2=db.Attendance()
        # self.obj3=DetectFace()
        self.obj4=db.Student()

        self.cap=None
        self.camera_on=False
        self.camera_thread=None
        self.camLabel=None
        self.last_detected_id=None
        self.is_updating=False

        self.title("Strange Face")
        self.geometry("800x650+200+30")
        self.resizable(True, True)

        self.MainPage()

    def loginFrame(self,AdminPage):
        task=Task()
        bg = Image.open("data/images/loginBg.jpg")
        load = ctk.CTkImage(light_image=bg, size=(800, 650))

        self.main = ctk.CTkFrame(self.mainpage, width=800, height=650)
        self.main.grid(row=0, column=0)

        self.label = ctk.CTkLabel(self.main, width=800, height=650, text="", image=load)
        self.label.grid(row=0, column=0, sticky="snew")
        self.login = ctk.CTkFrame(self.main, width=350, height=550, fg_color="White", corner_radius=0)
        self.login.grid(row=0, column=0)

        lock = ctk.CTkImage(light_image=(Image.open("data/images/lock.png")), size=(250, 250))
        self.top = ctk.CTkFrame(self.login, width=350, height=250, fg_color="#000b8e", corner_radius=0)
        self.top.place(x=0, y=0)

        self.lock = ctk.CTkLabel(self.top, width=250, height=250, text="", image=lock)
        self.lock.place(x=60, y=0)

        self.wel = ctk.CTkLabel(
            self.login, text="Welcome", font=("Roboto", 24, "bold"), 
            text_color="black", height=40, width=200, corner_radius=20
        )
        self.wel.place(x=80, y=270)

        self.name = ctk.CTkEntry(self.login, placeholder_text="Username", height=40, width=250, corner_radius=20)
        self.name.place(x=50, y=320)

        self.password = ctk.CTkEntry(self.login, placeholder_text="Password", height=40, width=250, corner_radius=20,show="*")
        self.password.place(x=50, y=380)

        self.logbtn = ctk.CTkButton(
            self.login, text="login", height=30, width=100, fg_color="#020c84", 
            text_color="white", corner_radius=20, hover=False, cursor="hand2",
            command=lambda:self.processlogin(AdminPage,self.name.get(),self.password.get())
        )
        self.logbtn.place(x=130, y=440)

        backBtn=ctk.CTkImage(light_image=(Image.open("data/images/back.png")),size=(50,50))
        self.backBtn=ctk.CTkButton(self.main,width=50,height=50,fg_color="#192f3d",corner_radius=0,
            image=backBtn,text="",hover=False,cursor="hand2",command=lambda:task.back(self.main))
        self.backBtn.place(x=0,y=0)
    
    def processlogin(self,AdminPage,username,password):
        check=self.obj1.login(self.db,username,password)
        if check:
            AdminPage()
        else:
            messagebox.showerror("Error","Invalid Username or Password")
    
    def switch_camera(self,regno,name,pic,rtype):
        if self.switch_var.get()==1:
            if not self.camera_on:
                self.camera_on=True
                self.camera_thread=threading.Thread(target=self.Camera,args=(regno,name,pic,rtype))
                self.camera_thread.start()
        else:
            self.stop_camera()

    def Camera(self,regno,name,pic,rtype):
        if self.camera_on:
            img_cv2=self.obj3.CompareFace()

            img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
            img = ctk.CTkImage(light_image=img_pil, size=(370, 370))

            self.camLabel.configure(image=img)
            self.camLabel.image = img 
            self.UpdateStatusLabel(regno,name,pic,rtype)
            self.camLabel.after(10, lambda : self.Camera(regno,name,pic,rtype))

    def stop_camera(self):
        self.camera_on=False
        # self.obj3.cam.release()
        img=Image.new('RGB',(380,380),(4, 39, 96))
        blue_image=ctk.CTkImage(light_image=img,size=(370,370))
        self.camLabel.configure(image=blue_image)

        self.camLabel.update_idletasks()

    def UpdateStatusLabel(self, regno, name, pic,rtype):
        result = self.obj4.getAttendanceBanner(self.db, self.obj3.detected_id)

        if  self.is_updating or self.last_detected_id == self.obj3.detected_id:
            return
        
        if result:
            self.is_updating=True
            
            regno.configure(text="ID : " + str(result[0][0]))
            name.configure(text=str(result[0][1]))

            self.obj2.MarkAttendance(self.db,str(result[0][0]))

            img = ctk.CTkImage(light_image=Image.open(f"data/StudentPictures/{result[0][0]}.jpg"), size=(180, 180))
            pic.configure(image=img)

            rtype.configure(text="Role : Student")
            
            self.status.after(10000, lambda: self.reset_status(regno, name, pic,rtype))
            
    def reset_status(self, regno, name, pic,rtype):
        if self.is_updating:
            regno.configure(text="")
            name.configure(text="")
            rtype.configure(text="")
            pic.configure(image=None)

            self.is_updating=False
            self.last_detected_id=None
    
    def open_submenu(self):
        x = self.export.winfo_x()
        y = self.export.winfo_y()

        menu_x = self.menu.winfo_x() + x+245
        menu_y = self.menu.winfo_y() + self.export.winfo_height()+95

        self.MenuBar.tk_popup(menu_x, menu_y)

    
    def MainPage(self):
        self.mainpage = ctk.CTkFrame(
            self, width=800, height=650, fg_color="#f1faee", corner_radius=0
        )
        self.mainpage.place(x=0, y=0)

        adm = Admin(self.mainpage)
        atd = Attendance(self.mainpage)
        task = Task()
        
        self.header = ctk.CTkFrame(
            self.mainpage, width=800, height=120, fg_color="#141f68",corner_radius=0)
        self.header.place(x=0, y=0)

        self.title = ctk.CTkLabel(self.header, text="Welcome To Strange Face",
            text_color="white",font=("Arial Black",30,"bold"))
        self.title.place(x=10, y=30)

        mainHead = ctk.CTkImage(light_image=(Image.open("data/images/mainHead.png")), size=(120, 120))
        
        self.mainhead=ctk.CTkLabel(self.header,width=150,height=130,fg_color="#141f68",text="",image=mainHead)
        self.mainhead.place(x=600,y=0)

        self.body=ctk.CTkFrame(self.mainpage,width=780,height=530,fg_color="white",border_color="black",
            border_width=3)
        self.body.place(x=10,y=135)

        self.camLabel = ctk.CTkLabel(self.body, width=410, height=400, text="", fg_color="#042760", corner_radius=20)
        self.camLabel.place(x=25, y=40)

        self.switch_var=ctk.IntVar()

        self.toggle_camera=ctk.CTkSwitch(self.body,text="",variable=self.switch_var,onvalue=1,offvalue=0,
            command=lambda:self.switch_camera(self.reg,self.name,self.pic,self.type))
        self.toggle_camera.place(x=270,y=5)

        self.status = ctk.CTkFrame(
            self.body, width=300, height=400, corner_radius=20, fg_color="#a8dadc"
        )
        self.status.place(x=450, y=40)

        self.pic = ctk.CTkLabel(self.status, width=200, height=200, corner_radius=10, fg_color="#141f68", text="")
        self.pic.place(x=50, y=10)

        self.reg = ctk.CTkLabel(
            self.status, width=200, height=30, font=("Helvetica", 15, "bold"), 
            text="", text_color="white",fg_color="#141f68",
            corner_radius=20
        )
        self.reg.place(x=50, y=300)

        self.name = ctk.CTkLabel(
            self.status, width=200, height=40, font=("Courier New", 20, "bold"), 
            text="", text_color="black"
        )
        self.name.place(x=50, y=240)

        self.type = ctk.CTkLabel(
            self.status, width=200, height=30, font=("Helvetica", 15 , "bold"), 
            text="", text_color="white",fg_color="#141f68",
            corner_radius=20
        )
        self.type.place(x=50, y=350)

        self.menu = ctk.CTkFrame(self.body, width=780, height=50, corner_radius=0,fg_color="#141f68",
            border_color="black",border_width=3)
        self.menu.place(x=0, y=465)

        self.view = ctk.CTkButton(
            self.menu, width=130, height=30, text="View Attendance", text_color="white", fg_color="#3746c3", 
            corner_radius=10, hover=False, cursor="hand2", font=("Roboto", 14, "bold"),command=atd.viewAttendancePage
        )
        self.view.place(x=50, y=10)

        self.export = ctk.CTkButton(
            self.menu, width=130, height=30, text="Export Attendance", text_color="white", fg_color="#3746c3", 
            corner_radius=10, hover=False, cursor="hand2", font=("Roboto", 14, "bold"),
            command=self.open_submenu
        )
        self.export.place(x=230, y=10)

        DateData=self.obj2.getDate(self.db)

        self.MenuBar=tk.Menu(self.menu,tearoff=0)
        
        for i in DateData:
            self.MenuBar.add_command(label=i,command=lambda date=i : atd.exportAttendance(date))
            self.MenuBar.add_separator()
        
        self.MenuBar.add_command(label="All",command=lambda:atd.exportAttendance("All"))

        self.admin = ctk.CTkButton(
            self.menu, width=130, height=30, text="Admin Panel", text_color="white", fg_color="#3746c3", 
            corner_radius=10, hover=False, cursor="hand2", font=("Roboto", 14, "bold"), 
            command=lambda : self.loginFrame(adm.AdminPage)
        )
        self.admin.place(x=430, y=10)

        self.reset = ctk.CTkButton(
            self.menu, width=130, height=30, text="Reset", text_color="white", fg_color="#3746c3", 
            corner_radius=10, hover=False, cursor="hand2", font=("Roboto", 14, "bold"),
            command=task.Reset
        )
        self.reset.place(x=610, y=10)
        
class Admin:
    def __init__(self, mainpage):
        self.setPage = mainpage
        self.task=Task()
        self.db=db.Database()
        self.obj1=db.Admin()
        self.obj3=db.Student()
    
    def AdminPage(self):

        admHead=ctk.CTkImage(light_image=(Image.open("data/images/admHead.png")),size=(150,130))

        self.adminpage = ctk.CTkFrame(self.setPage, width=800, height=650, fg_color="white")
        self.adminpage.place(x=0,y=0)

        self.header = ctk.CTkFrame(
            self.adminpage, width=800, height=130, fg_color="#141f68",corner_radius=0)
        self.header.place(x=0, y=0)

        self.heading=ctk.CTkLabel(self.header,width=100,height=40,fg_color="#141f68",text="Welcome To Admin Panel",
            text_color="white",font=("Arial Black",30,"bold"))
        self.heading.place(x=80,y=40)

        self.admhead=ctk.CTkLabel(self.header,width=150,height=130,fg_color="#141f68",text="",image=admHead)
        self.admhead.place(x=600,y=0)

        self.body=ctk.CTkFrame(
            self.adminpage,width=770,height=480,fg_color="white",border_color="black",border_width=3)
        self.body.place(x=15,y=150)
        
        self.regno=ctk.CTkEntry(
            self.body,width=250,height=40,placeholder_text="Registration Number",corner_radius=10,
            font=("Arial",14,"bold"))
        self.regno.place(x=50,y=50)

        self.name=ctk.CTkEntry(
            self.body,width=250,height=40,placeholder_text="Student Name",corner_radius=10,
            font=("Arial",14,"bold"))
        self.name.place(x=50,y=110)

        self.phone=ctk.CTkEntry(
            self.body,width=250,height=40,placeholder_text="Phone Number",corner_radius=10,
            font=("Arial",14,"bold"))
        self.phone.place(x=50,y=170)

        self.email=ctk.CTkEntry(
            self.body,width=250,height=40,placeholder_text="Email Address",corner_radius=10,
            font=("Arial",14,"bold"))
        self.email.place(x=50,y=230)

        self.pic=ctk.CTkLabel(
            self.body,width=150,height=150,text="",corner_radius=0,fg_color="#484849")
        self.pic.place(x=500,y=50)

        self.infoLabel=ctk.CTkLabel(self.body,width=150,height=30,text="",
            text_color="#ea2a17",fg_color="White",font=("Arial",14,"bold"))
        self.infoLabel.place(x=430,y=220)
    
        self.uploadBtn=ctk.CTkButton(self.body,width=150,height=150,text="Upload Picture",corner_radius=0,
            fg_color="#484849",text_color="white",hover=False,cursor="hand2",font=("Arial",14,"bold"),
            command=lambda:self.task.ProcessImage(self.pic,self.uploadBtn,self.infoLabel,self.regBtn,self.regno.get()))
        self.uploadBtn.place(x=500,y=50)

        self.regBtn=ctk.CTkButton(self.body,width=150,height=40,text="Register User",corner_radius=10,
            fg_color="#0c0c70",text_color="white",hover=False,cursor="hand2",font=("Arial",14,"bold"),
            command=lambda:self.processReg(self.regno.get(),self.name.get(),self.email.get(),self.phone.get(),self.pic),
            state="disabled")
        self.regBtn.place(x=200,y=300)
        
        backBtn=ctk.CTkImage(light_image=(Image.open("data/images/back.png")),size=(50,50))
        self.backBtn=ctk.CTkButton(self.header,width=50,height=50,fg_color="#141f68",corner_radius=0,
            image=backBtn,text="",hover=False,cursor="hand2",command=lambda:self.task.back(self.adminpage))
        self.backBtn.place(x=0,y=0)

        self.checkUser = ctk.CTkButton(
            self.body, width=130, height=30, text="Registered Users", text_color="#0c0c70", fg_color="white", 
            corner_radius=10, hover=False, cursor="hand2", font=("Roboto", 14, "bold"),
            command=self.viewUsersPage
        )
        self.checkUser.place(x=10, y=440)

    def processReg(self,reg,name,email,phone,imageLabel):
        result=self.obj3.UserExist(self.db,reg)
        if (reg=="" or name=="" or email=="" or phone==""):
            messagebox.showerror("Error","Some Fields Are Missing")
        elif result:
            messagebox.showerror("Error","Registration Number already Exists")
        else:
            self.obj3.register(self.db,reg,name,email,phone)
            messagebox.showinfo("Success","Registration Successful")
            self.task.back(self.adminpage)
            self.AdminPage()
    
    def viewUsersPage(self):
        task=Task()
        
        regHead=ctk.CTkImage(light_image=(Image.open("data/images/regHead.png")),size=(130,130))
        self.regpage = ctk.CTkFrame(self.setPage, width=800, height=650, fg_color="white")
        self.regpage.place(x=0,y=0)

        self.header = ctk.CTkFrame(
            self.regpage, width=800, height=130, fg_color="#141f68",corner_radius=0)
        self.header.place(x=0, y=0)

        self.heading=ctk.CTkLabel(self.header,width=100,height=40,fg_color="#141f68",text="Registered Users",
            text_color="white",font=("Arial Black",30,"bold"))
        self.heading.place(x=80,y=40)

        self.reghead=ctk.CTkLabel(self.header,width=330,height=130,fg_color="#141f68",text="",image=regHead)
        self.reghead.place(x=500,y=0)

        backBtn=ctk.CTkImage(light_image=(Image.open("data/images/back.png")),size=(50,50))
        self.backBtn=ctk.CTkButton(self.header,width=50,height=50,fg_color="#141f68",corner_radius=0,
            image=backBtn,text="",hover=False,cursor="hand2",command=lambda:task.back(self.regpage))
        self.backBtn.place(x=0,y=0)

        self.body=ctk.CTkScrollableFrame(
                self.regpage,width=765,height=480,fg_color="white")
        self.body.place(x=15,y=150)
        
        self.viewRegUsers(self.body)

    def viewRegUsers(self,frame):
        columns=["Registration No","Name","Reg Date","Phone","Email"]
        tree=ttk.Treeview(frame,columns=columns,show="headings",height=50)

        style=ttk.Style()
        style.configure("Treeview.Heading",font=("Arial Black",12,"bold"))

        for col in columns:
            tree.heading(col,text=col)
            if col in ("Registration No","Name","Reg Date","Phone"):
                tree.column(col,anchor="center",width=72)
            else:
                tree.column(col,anchor="center",width=120)
            
        data=self.obj3.getUsers(self.db)

        if data:
            for row in data:
                tree.insert("","end",values=row)
            
        tree.pack(fill="both", expand=True)

class Attendance:
    def __init__(self,mainframe):
        self.setPage=mainframe
        self.db=db.Database()
        self.obj1=db.Attendance()
        self.pdf=FPDF()

    def viewAttendancePage(self):
        task=Task()

        atdHead=ctk.CTkImage(light_image=(Image.open("data/images/attendance.png")),size=(130,130))

        self.Attendancepage = ctk.CTkFrame(self.setPage, width=800, height=650, fg_color="white")
        self.Attendancepage.place(x=0,y=0)

        self.header = ctk.CTkFrame(
            self.Attendancepage, width=800, height=130, fg_color="#141f68",corner_radius=0)
        self.header.place(x=0, y=0) 

        value=["All"] 
        a=self.obj1.getDate(self.db)
        if a:
            for i in a:
                i=str(i)
                value.append(i[2:-3])
        
        self.day=ctk.CTkOptionMenu(self.header,values=value,width=140,height=30,text_color="white",fg_color="#141f68",
            corner_radius=0,font=("Arial Black",16,"bold"),command=self.option_select)
        self.day.place(x=300)

        self.day.set(value[0])

        self.heading=ctk.CTkLabel(self.header,width=100,height=40,fg_color="#141f68",text="Welcome To Attendance Panel",
            text_color="white",font=("Arial Black",30,"bold"))
        self.heading.place(x=40,y=70)

        self.atdhead=ctk.CTkLabel(self.header,width=330,height=130,fg_color="#141f68",text="",image=atdHead)
        self.atdhead.place(x=560,y=0)

        backBtn=ctk.CTkImage(light_image=(Image.open("data/images/back.png")),size=(50,50))
        self.backBtn=ctk.CTkButton(self.header,width=50,height=50,fg_color="#141f68",corner_radius=0,
            image=backBtn,text="",hover=False,cursor="hand2",command=lambda:task.back(self.Attendancepage))
        self.backBtn.place(x=0,y=0)

        self.body=ctk.CTkScrollableFrame(
                self.Attendancepage,width=765,height=480,fg_color="white")
        self.body.place(x=15,y=150)
        
        self.data=self.obj1.getAttendance(self.db)
        self.viewAttendance(self.body,self.data)
        
    def option_select(self,value):
        if value == "All":
             self.data=self.obj1.getAttendance(self.db)
        else:
            self.data = self.obj1.GetSpecific(self.db,value)
        
        data=self.data
        self.viewAttendance(self.body,data)
    
    def viewAttendance(self, frame,data):
        if not hasattr(self, 'tree'):
            columns = ["Registration No", "Name", "Date", "Status"]
            self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=50)

            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Arial Black",12,"bold"))

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            self.tree.pack(fill="both", expand=True)

        for row in self.tree.get_children():
            self.tree.delete(row)

        if data:
            for row in data:
                self.tree.insert("", "end", values=row)


    def generatedTime(self):

        self.time=datetime.now()
        self.time=self.time.strftime("%I:%M:%p")
        self.pdf.set_y(5)
        self.pdf.set_font("Arial","B",10)

        self.pdf.cell(0,10,f'Generated at : '+str(self.time),ln=True,align="L")
    
    def footer(self):
        self.pdf.set_y(-15)
        self.pdf.set_font("Arial","I",12)

        self.pdf.cell(0,10,'Page'+self.pdf.page_no(),0,0,"C")
        
    def exportAttendance(self,value):

        if value == "All":
            data=self.obj1.getAttendance(self.db)
        else:
            value=value[0]
            data = self.obj1.GetSpecific(self.db,value)
        
        self.pdf.set_auto_page_break(auto=True,margin=15)
        self.pdf.add_page()
        self.generatedTime()
        self.pdf.set_font("Arial","B",16)

        self.pdf.cell(200,10,"Attendance Sheet",ln=True,align="C")
        self.pdf.set_font("Arial","B",12)

        self.pdf.cell(40,10,"Arid No",border=1)
        self.pdf.cell(60,10,"Student Name",border=1)
        self.pdf.cell(40,10,"Date",border=1)
        self.pdf.cell(30,10,"Status",border=1)
        self.pdf.ln()

        self.pdf.set_font("Arial","",12)
        if data:
            for row in data:
                a,b,c,d=row
                self.pdf.cell(40,10,a,border=1)
                self.pdf.cell(60,10,b,border=1)
                self.pdf.cell(40,10,c,border=1)
                self.pdf.cell(30,10,d,border=1)
                self.pdf.ln()
        
        self.pdf.output("output/Attendance Sheet.pdf")
        messagebox.showinfo("Sucess","Attendance Sheet Exported Successfully")

if __name__ == "__main__":
    app = MyApp()
    app.mainpage()
    app.mainloop()
