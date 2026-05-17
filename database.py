import mysql.connector
from mysql.connector import Error
from abc import ABC,abstractmethod
import hashlib
import datetime as dt

class Database:
    def __init__(self) :
        try:
            self.__mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                password="Stranger0556R",
                database="strangeface"
            )
            if self.__mydb.is_connected():
                print("Connected to the Database")
        except Error as e:
            print(f"Error Connecting to the Database : {e}")
            self.__mydb=None
    
    def execute_query(self,query,params=None) :
        try:
            cursor=self.__mydb.cursor()
            cursor.execute(query,params)
            self.__mydb.commit()
        except Error as e:
            print(f"Error Executing Query : {e}")
        finally:
            cursor.close()
    
    def fetch_result(self,query,params=None) :
        try:
            cursor=self.__mydb.cursor()
            cursor.execute(query,params)
            result=cursor.fetchall()
            return result
        except Error as e:
            print(f"Error Fetching Results : {e}")
        finally:
            cursor.close()
    
    def  close_connection(self) :
        if self.__mydb and self.__mydb.is_connected():
            self.__mydb.close()
            print("Connection to the Database is Closed")
        
class Admin:
    def __init__(self) :
        self.username=""
        self.password=""
    
    def login(self,db,username,password) :
        self.username=username
        self.password=password

        query="""SELECT username,password
                 FROM admins 
                 WHERE username=%s AND password=%s"""
        params=(self.username,self.password)
        result=db.fetch_result(query,params)
        if result:
            return True
            print("Login Successfull")
        else:
            return False
    
    def ClearAll(self,db):
        query="""DELETE FROM student;
                DELETE FROM attendance;
                """
        db.execute_query(query)

class Student:
    def __init__(self) :
        self.regno=""
        self.name=""
        self.email=""
        self.phone=""
        self.reg_date=""
    
    def register(self,db,reg_no,name,email,phone):
        self.regno=reg_no
        self.name=name
        self.email=email
        self.phone=phone
        self.reg_date=dt.datetime.now().date()

        query="""INSERT INTO student (reg_no , name , email , phone , reg_date)
                 VALUES (%s,%s,%s,%s,%s)"""
        params=(self.regno,self.name,self.email,self.phone,self.reg_date)

        db.execute_query(query,params)
    
    def getUsers(self,db):
        query="""SELECT reg_no,name,reg_date,phone,email
                 FROM student """
        
        result=db.fetch_result(query)

        if result:
            return result
        else:
            return
    
    def UserExist(self,db,regno):
        query="""SELECT* FROM student
                 WHERE reg_no=%s"""
        params=(regno,)

        result=db.fetch_result(query,params)
        if result:
            return True
        else:
            return False
    
    def getAttendanceBanner(self,db,Aridno):
        query="""SELECT reg_no,name
              FROM student
              WHERE reg_no=%s"""
        params=(Aridno,)

        result=db.fetch_result(query,params)

        if result:
            return result
        else:
            return None

class Attendance:
    def __init__(self):
        self.student_id=""
        self.Attendance_date=""
        self.status=""
    
    def MarkAttendance(self,db,sid):
        self.student_id=sid
        self.Attendance_date=dt.datetime.now().date()
        self.status="Present"

        query="""INSERT INTO attendance (s_id , date , status)
                 VALUES (%s,%s,%s)"""
        params=(self.student_id,self.Attendance_date,self.status)

        result=self.checkDate(db,sid)
        
        if result:
            print("Attendance Already Marked")
        else:
            db.execute_query(query,params)
            
    def getAttendance(self,db):
        query="""SELECT s.reg_no,s.name,a.date,a.status
                 FROM student s
                 INNER JOIN attendance a
                 ON s.reg_no=a.s_id"""
        
        result=db.fetch_result(query)

        if result:
            return result
        else:
            return
        
    def getDate(self,db):
        query="""SELECT DISTINCT date FROM
              attendance"""
        result=db.fetch_result(query)

        formatted_Date=[]
        if result:
            return result
        else:
            return None
        
    def GetSpecific(self,db,date):

        print(date)

        query="""SELECT s.reg_no,s.name,a.date,a.status
                 FROM student s
                 INNER JOIN attendance a
                 ON s.reg_no=a.s_id
                 WHERE a.date=%s"""
        date=str(date)
        params=(date,)

        result=db.fetch_result(query,params)

        if result:
            return result
        else:
            return
    def checkDate(self,db,sid):
        today=dt.datetime.now().date()
        query="""SELECT* FROM
              attendance 
              WHERE s_id=%s AND date=%s"""
        params=(sid,today)

        result=db.fetch_result(query,params)

        if result:
            return True
        else:
            return False
    

    

        
