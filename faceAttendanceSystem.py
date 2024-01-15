from bson import ObjectId
import customtkinter as ctk
import cv2
from datetime import datetime, timedelta
from PIL import Image
import face_recognition
import pygame
import pymongo
from CTkMessagebox import CTkMessagebox
from tkinter import ttk, filedialog
import csv
from tkcalendar import DateEntry
import hashlib
import ctypes
import sys

import constants



class App:
    def __init__(self):

        ctk.set_appearance_mode(constants.appApperanceMode)
        ctk.set_default_color_theme(constants.appDefaultColorTheme)
        self.root = ctk.CTk()
        self.root.geometry(constants.appGeometry + constants.appPosition)
        self.root.resizable(width=False, height=False)
        self.root.title(constants.appTitle)
        self.cap = cv2.VideoCapture(0)

        self.buildFrontend_sidebar()
        self.buildFrontend_mainFrame()
        self.buildFrontend_sidebar_mainPage() #create initially the mainPage sidebar
        
        # Connect to MongoDB
        self.client = pymongo.MongoClient(constants.mongodbHostAdress)
        self.db = self.client[constants.databaseName]
        self.collection_users = self.db[constants.userCollection]
        self.collection_attendancy = self.db[constants.attendancyCollection]
        self.collection_admins = self.db[constants.adminCollection]

        self.addAdminAccountOnce()




    def buildFrontend_sidebar(self):
        self.option_frame = ctk.CTkFrame(self.root, fg_color='#292727', bg_color='#292727')
        self.option_frame.pack(side=ctk.LEFT)
        self.option_frame.pack_propagate(False)
        self.option_frame.configure(height=620, width=150)


    def buildFrontend_mainFrame(self):
        self.main_frame = ctk.CTkFrame(self.root, border_color='black', border_width=5)
        self.main_frame.pack(side=ctk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=620, width=1100)


    def buildFrontend_sidebar_mainPage(self):
        
        #Take Attendancy Button
        self.takeAttendance_btn = ctk.CTkButton(self.option_frame,text='Take\nAttendancy',font=('Bold', 15),fg_color='#292727',bg_color='#292727',text_color='#158aff',hover=False,corner_radius=0,border_width=0,width=150,height=35,
            command=lambda: self.indicate(self.takeAttendance_indicate, self.hide_indicators_mainPage, self.takeAttendance_page))
        self.takeAttendance_btn.pack(pady=20)
        self.takeAttendance_indicate =  ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.takeAttendance_indicate.place(x=3, y=20)

        # AttendancyInfo Button
        self.attendancyInfo_btn = ctk.CTkButton(self.option_frame, text='Info\nAttendancy', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover=False, corner_radius=0, border_width=0, width=150, height=35,
                                           command=lambda: self.indicate(self.attendancyInfo_indicate, self.hide_indicators_mainPage, self.attendancyInfo_page)) 
        self.attendancyInfo_btn.pack(pady=20)
        self.attendancyInfo_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.attendancyInfo_indicate.place(x=3, y=100)

        # Admin Button
        self.register_btn = ctk.CTkButton(self.option_frame, text='Administration', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover=False, corner_radius=0, border_width=0, width=150, height=35,
                                           command=lambda: self.indicate(self.admin_indicate, self.hide_indicators_mainPage, self.admin_page)) 
        self.register_btn.pack(pady=20)
        self.admin_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=34)
        self.admin_indicate.place(x=3, y=180)

        self.takeAttendance_btn.invoke()  #invoke takeAttendance Button after building sidebar in main page


    
    
    def buildFrontend_sidebar_adminPage(self):

        #Add user button
        self.add_user_button = ctk.CTkButton(self.option_frame, text='Register User', font=('Bold', 15), fg_color='#292727',
                                          bg_color='#292727', text_color='#158aff', hover=False,
                                          corner_radius=0, border_width=0, width=150, height=35,
                                          command=lambda: self.indicate(self.add_user_indicate, self.hide_indicators_adminPage, self.register_page))
        self.add_user_button.pack(pady=20)
        self.add_user_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=34)
        self.add_user_indicate.place(x=3, y=20)

        #List Users Button
        self.list_users_btn = ctk.CTkButton(self.option_frame, text='List Users', font=('Bold', 15), fg_color='#292727',
                                            bg_color='#292727', text_color='#158aff', hover=False,
                                            corner_radius=0, border_width=0, width=150, height=35,
                                            command=lambda: self.indicate(self.list_users_indicate, self.hide_indicators_adminPage ,self.list_users))
    
        self.list_users_btn.pack(pady=20)
        self.list_users_indicate= ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=34)
        self.list_users_indicate.place(x=3, y=95)

        #Back to Main Button
        self.logout_admin_btn = ctk.CTkButton(self.option_frame, text='Back to main', font=('Bold', 15), fg_color='#292727',
                                            bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                            corner_radius=0, border_width=0, width=150, height=35,
                                            command=self.logout_admin)
        
        self.logout_admin_btn.pack(pady=20)

        self.add_user_button.invoke()  #invoke add_user_button Button after building sidebar in admin page





    # possiblity to create admin accounts 
    def createAdminAccount(self, username, password):
        
        adminAccData = {
            constants.usernameAdminAttr : username,
            constants.passwordAdminAtrr : hashlib.sha256(password.encode()).hexdigest()
        }
        self.collection_admins.insert_one(adminAccData)


    #Adding Admin Account with username "admin" and password "admin" once
    #It will only be created if in the database the admin collection is not already created
    def addAdminAccountOnce(self):
        if self.collection_admins.name not in self.db.list_collection_names():
            self.createAdminAccount(constants.adminUsername, constants.adminPassword)
    


    def register_attendancy(self, _userId, startOrEnd):
        timestamp = datetime.now()

        attendancy_data = {
             constants.userIdAttr: _userId,
             constants.timeStampAttr: timestamp,
             constants.statusAttr: startOrEnd
        }
        
        self.collection_attendancy.insert_one(attendancy_data)
         


    def check_status_before_register_attendancy(self, _userId, statusToCheck):

        if _userId and statusToCheck:
            
            query = {constants.userIdAttr: _userId}
            if self.collection_attendancy.count_documents(query):
                user = self.collection_attendancy.find(query)
                if user:
                    sort_order = [(constants.timeStampAttr, pymongo.DESCENDING)]
                    userLastElement = next(user.sort(sort_order).limit(1))

                    if userLastElement and userLastElement[constants.statusAttr] == statusToCheck:
                        return True
            else:
                if(statusToCheck == "End"):
                    return True

        return False



    def playSoundInTakingAttendancy(self, filename):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

    

    def start_working(self):
        db_user_id = self.find_userID_by_picture()
        
        if db_user_id:
            db_user_name = self.find_dataObj_by_id(db_user_id, constants.nameUserAttr)
            if self.check_status_before_register_attendancy(db_user_id, "End"):
                self.register_attendancy(db_user_id, 'Start')
                self.playSoundInTakingAttendancy(constants.startWorkingSound)
                CTkMessagebox(title="Welcome", message=f"Welcome to work, {db_user_name}!", icon='check')
            else:
               CTkMessagebox(title="Error", message=f"{db_user_name}, you have already started your work, please end it before restarting", icon="cancel") 
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")


    
    def end_working(self):
        db_user_id = self.find_userID_by_picture()

        if db_user_id:
            db_user_name = self.find_dataObj_by_id(db_user_id, constants.nameUserAttr)
            if self.check_status_before_register_attendancy(db_user_id, "Start"):
                self.register_attendancy(db_user_id, 'End')
                self.playSoundInTakingAttendancy(constants.endWorkingSound)
                CTkMessagebox(title="Goodbye", message=f"Goodbye, {db_user_name}!", icon='check')
            else:
                 CTkMessagebox(title="Error", message=f"{db_user_name}, you have already ended your work, please start it before ending", icon="cancel") 
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")

     

    def find_dataObj_by_id(self, _userId, dataAttr):

        if _userId:
            query = {constants.idAttr: _userId}

            user = self.collection_users.find_one(query)

            if user:
                if user[dataAttr]:
                    return user[dataAttr]
       
        return None

    

    def find_userID_by_picture(self):

        ret, frame = self.cap.read()

        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_locations and face_encodings:
                user_face_encoding = face_encodings[0]

                all_users = self.collection_users.find()

                for user in all_users:

                    db_user_id = user[constants.idAttr]
                    db_face_encoding = user[constants.faceEncodingUserAttr]

                    match = face_recognition.compare_faces([db_face_encoding], user_face_encoding)

                    if any(match):
                        return db_user_id
        return None
        


    def saveAttendancyInfoAsCSV(self, table, rootWindow):

        if not table.get_children():
            CTkMessagebox(title="Error", message="No Data in table to download as CSV", icon="cancel")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], parent=rootWindow)
        headings = [table.heading(column_id)['text'] for column_id in table["columns"]]
        if filepath:
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(headings)

                for item in table.get_children():
                    writer.writerow(table.item(item, option="values"))
            print(f"CSV file saved to: {filepath}")


    def getFilteredDatesAndTime(self, userId,attendancy_table, startDate_filter, endDate_filter):
        
        self.delete_content_of_table(attendancy_table)

        start_date = datetime.strptime(startDate_filter.get(), "%d.%m.%Y")
        end_date =  datetime.strptime(endDate_filter.get(), "%d.%m.%Y") + timedelta(days=1)
 
        if start_date < end_date:
        
            query = {constants.userIdAttr:userId, constants.timeStampAttr:{"$gte": start_date, "$lte": end_date}}
            results = self.collection_attendancy.find(query)

            if self.collection_attendancy.count_documents(query) != 0:
                for result in results:
                    date = result[constants.timeStampAttr].strftime("%d.%m.%Y")
                    time = result[constants.timeStampAttr].strftime("%H:%M:%S")
                    dataset = (date, self.find_dataObj_by_id(userId, constants.nameUserAttr),self.find_dataObj_by_id(userId, constants.departmentUserAttr) , time, result[constants.statusAttr]) #self.find_dataObj_by_id(userId, constants.departmentAttr)
                    dataset_id = attendancy_table.insert("", "end", values=dataset)
                    if result[constants.statusAttr] == "Start":
                        attendancy_table.tag_configure(f"{dataset_id}", background="green")
                        attendancy_table.item(dataset_id, tags=(f"{dataset_id}",))
                    else:
                        attendancy_table.tag_configure(f"{dataset_id}", background="red")
                        attendancy_table.item(dataset_id, tags=(f"{dataset_id}",))

            else:
                 CTkMessagebox(title="Error", message="No Data found", icon="cancel")
        else:
             CTkMessagebox(title="Error", message="Invalid Dates", icon="cancel")

    
    #Currently not in use, but after extension of the userinterface to two datepickers, this function can be used
    #to clear the attendancy collection
    def clearAttendancyCollection(self ,start_date_entry, end_date_entry):

        start_date = datetime.strptime(start_date_entry.get(), "%d.%m.%Y")
        end_date =  datetime.strptime(end_date_entry.get(), "%d.%m.%Y") + timedelta(days=1)

        if start_date < end_date:
            query = {constants.timeStampAttr:{"$gte": start_date, "$lte": end_date}}
            self.collection_attendancy.delete_many(query)
        else:
            CTkMessagebox(title="Error", message="Invalid Dates", icon="cancel")



    def newWindow_attendancyInfo(self, userId):
        attendancyInfo_window = ctk.CTkToplevel(self.root)
        attendancyInfo_window.geometry(constants.appGeometry)
        attendancyInfo_window.resizable(width=False, height=False)
        attendancyInfo_window.title(f"Attendancy Information of {self.find_dataObj_by_id(userId, constants.nameUserAttr)}")
        attendancyInfo_window.attributes("-topmost", True)

        attendancyInfo_frame = ctk.CTkFrame(attendancyInfo_window)
        attendancyInfo_frame.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")

        style = ttk.Style(attendancyInfo_window)
        style.theme_use("clam")
        style.configure("Custom1.Treeview", background="black", fieldbackground="black", foreground="white")
        attendancy_table = ttk.Treeview(attendancyInfo_frame, columns=("date", "name", "department", "time","status"), show="headings",height=300, selectmode='none', style="Custom1.Treeview")
        
        attendancy_table.heading("date", text="Date")
        attendancy_table.heading("name", text="Name")
        attendancy_table.heading("department", text="Department")
        attendancy_table.heading("time", text="Time")
        attendancy_table.heading("status", text="Status")
        attendancy_table.pack(side=ctk.LEFT)

        sb = ttk.Scrollbar(attendancyInfo_frame, orient='vertical', command=attendancy_table.yview)
        sb.pack(side="right", fill="y")
        attendancy_table.configure(yscrollcommand=sb.set)

        start_filter_label = ctk.CTkLabel(attendancyInfo_frame, text="Start Date:")
        start_filter_entry = DateEntry(attendancyInfo_frame, width=12, background='darkblue', foreground='black', borderwidth=2, date_pattern='dd.mm.yyyy', parent=attendancyInfo_window)
        end_filter_label = ctk.CTkLabel(attendancyInfo_frame, text="End Date:")
        end_filter_entry = DateEntry(attendancyInfo_frame, width=12, background='darkblue', foreground='black', borderwidth=2, date_pattern='dd.mm.yyyy', parent=attendancyInfo_window)
        start_filter_label.pack(side=ctk.TOP, pady=(30,5), padx=20)
        start_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)
        end_filter_label.pack(side=ctk.TOP, pady=(150, 5), padx=20)
        end_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)

        filter_button = ctk.CTkButton(attendancyInfo_frame, text="Filter", command=lambda:self.getFilteredDatesAndTime(userId, attendancy_table, start_filter_entry, end_filter_entry), bg_color='green', fg_color='green', hover_color='#2b5c30')
        filter_button.pack(side=ctk.TOP, anchor='s', pady=(190, 0), padx=10)

        csvDownlaod_button = ctk.CTkButton(attendancyInfo_frame, text="Download Table\nas CSV", command=lambda:self.saveAttendancyInfoAsCSV(attendancy_table, attendancyInfo_window), bg_color='blue', fg_color='blue', hover_color='#09213d')
        csvDownlaod_button.pack(side=ctk.TOP, anchor='s', pady=(20, 0), padx=10)

        
    


    def delete_content_of_table(self, table):
        if(table):
            for item in table.get_children():
                table.delete(item)

 

    
    def loginUser_filterUserAttendancy(self):
        db_user_id = self.find_userID_by_picture()
        if db_user_id:
            self.newWindow_attendancyInfo(db_user_id)
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")
    



    def takeAttendance_page(self):

        takeAttendace_frame = ctk.CTkFrame(self.main_frame)
        takeAttendace_frame.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")
        cam_lb = ctk.CTkLabel(takeAttendace_frame, text='')
        cam_lb.pack(side=ctk.LEFT)
        self.add_webcam(cam_lb, 800, 620)

        start_work_btn = ctk.CTkButton(takeAttendace_frame, text="Start Work", bg_color='green', fg_color='green', hover_color='#2b5c30', width=500, height=260, command=self.start_working)
        start_work_btn.pack(side=ctk.TOP, pady=15, padx=20)

        end_work_btn = ctk.CTkButton(takeAttendace_frame, text="End Work", bg_color='red', hover_color='#5c1d1d', fg_color='red', width=500, height=260, command=self.end_working)
        end_work_btn.pack(side=ctk.TOP, anchor='s', pady=15, padx=20)


    def attendancyInfo_page(self):
        attendancyInfoLogin_frame = ctk.CTkFrame(self.main_frame)
        attendancyInfoLogin_frame.pack(pady=20, padx=20, side=ctk.TOP)
        cam_lb = ctk.CTkLabel(attendancyInfoLogin_frame, text='')
        cam_lb.pack(side=ctk.TOP)
        self.add_webcam(cam_lb, 700, 520)

        end_work_btn = ctk.CTkButton(attendancyInfoLogin_frame, text="See my Attendacy", bg_color='green', hover_color='#2b5c30', fg_color='green', width=600, height=260, command=self.loginUser_filterUserAttendancy)
        end_work_btn.pack(side=ctk.TOP, anchor='s', pady=15, padx=20)
        

   
    def admin_page(self):

        instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Admin credentials", font=('Bold', 20), text_color='white')
        instruction_label.pack(pady=(100, 10), padx=10)  

        adminname = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=100)
        adminname.pack(pady=10)
        adminpw = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=100, show='*')
        adminpw.pack(pady=10)
        login_btn = ctk.CTkButton(self.main_frame, text="Login", font=('Bold', 15), fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.login_admin(adminname.get(),adminpw.get()))
        login_btn.pack(pady=20)



    def login_admin(self,adminname,adminpw):

        query = {
            constants.usernameAdminAttr : adminname,
            constants.passwordAdminAtrr : hashlib.sha256((adminpw).encode()).hexdigest()
        }

        adminAccount = self.collection_admins.find_one(query)
        
        if adminAccount:
            self.delete_optionFrameContent()
            self.buildFrontend_sidebar_adminPage()

        else:
            CTkMessagebox(title="Error", message="Invalid admin credentials!", icon="cancel")

 

    def register_page(self):
        self.delete_mainFrameContent()

        instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Employee name", font=('Bold', 15), text_color='white')
        instruction_label.pack(pady=(50, 0), padx=10) 
        name = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=200)
        name.pack(pady=(10,30))

        department_instruction_label = ctk.CTkLabel(self.main_frame, text="Please Select The Department", font=('Bold', 15), text_color='white')
        department_instruction_label.pack(pady=(10,0))  
        department_combobox = ttk.Combobox(self.main_frame, values=constants.department_options, font=('Bold', 15), state="readonly")
        department_combobox.pack(pady=(10,30))

        birthdate_instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Birthdate", font=('Bold', 15), text_color='white')
        birthdate_instruction_label.pack(pady=(10,0))
        birthdate = DateEntry(self.main_frame, width=12, background='darkblue', foreground='black', borderwidth=2, date_pattern='dd.mm.yyyy', font=('Bold', 15))
        birthdate.pack(pady=(10,30))

        start_registration_btn = ctk.CTkButton(self.main_frame, text="Start Registration", font=('Bold', 15), fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.start_registration(name.get(), department_combobox.get(), birthdate.get()))
        start_registration_btn.pack(pady=50)


    def start_registration(self, name, department_combobox,birthdate):
    
        if name: 
            self.delete_mainFrameContent()
         
            cam_lb = ctk.CTkLabel(self.main_frame, text='')
            cam_lb.pack(side=ctk.LEFT, pady=20, padx=20)
            
            capture_btn = ctk.CTkButton(self.main_frame, text="Capture Image", fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.registerUserWithPicture(name, birthdate, department_combobox))
            capture_btn.pack(pady=(60, 0))
            
            self.add_webcam(cam_lb, 800, 600)    


    def registerUserWithPicture(self, name, birthdate, department):

        ret, frame = self.cap.read()

        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_locations and face_encodings:
                user_face_encoding = face_encodings[0]

                user_data = {
                    constants.nameUserAttr: name,
                    constants.faceEncodingUserAttr: list(user_face_encoding),
                    constants.birthdateUserAttr : birthdate,
                    constants.departmentUserAttr : department,
                }
                self.collection_users.insert_one(user_data)

                CTkMessagebox(title="Success", message=f"{name} is successfully registered in the database!", icon="check")

                self.list_users_btn.invoke()

                print(f"User {name} registered in MongoDB with Birthdate: {birthdate} and Department: {department}!")

            else:
                CTkMessagebox(title="Error", message="No face detected. Please try again.", icon="cancel")
        else:
            print("Error in reading Camera")


    def showAllUsersInTable(self, user_table):

        self.delete_content_of_table(user_table)
        all_users = self.collection_users.find()

        for user in all_users:
            user_id = user.get(constants.idAttr) 
            name = user.get(constants.nameUserAttr)
            birthdate = user.get(constants.birthdateUserAttr)
            department = user.get(constants.departmentUserAttr)

            user_table.insert("", "end", values=(user_id, name, birthdate, department, "DELETE"), tags=("action_button",))


    def list_users(self):
        self.delete_mainFrameContent()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom2.Treeview", background="black", fieldbackground="black", foreground="white")

        user_list_table = ttk.Treeview(self.main_frame, columns=("User ID", "User Name", "Date of Birth", "Department", "Action"), show="headings", height=40, style="Custom2.Treeview")

        user_list_table.heading("User ID", text="User ID")
        user_list_table.heading("User Name", text="User Name")
        user_list_table.heading("Date of Birth", text="Date of Birth")
        user_list_table.heading("Department", text="Department")
        user_list_table.heading("Action", text="Action")

        self.showAllUsersInTable(user_list_table)

        user_list_table.bind("<Button-1>", lambda event: self.handle_click_for_delete_action(event, user_list_table))
        user_list_table.pack(pady=20, padx=20)


    def handle_click_for_delete_action(self, event, user_table):

        item = user_table.selection()
        if item:
            column = user_table.identify_column(event.x)
            if column == "#5":  
                user_id = user_table.item(item, "values")[0]
                confirmationMsgBox = CTkMessagebox(title="Confirmation", message="Do you want to delete this user?", icon="question", option_1="No", option_2="Yes")
                response = confirmationMsgBox.get()
                if response == "Yes":
                    self.delete_user(user_id)


    def delete_user(self,user_id):

        print(f"Deleting user with ID: {user_id}")

        queryUserCollection = {constants.idAttr:ObjectId(user_id)}
        queryAttendancyCollection = {constants.userIdAttr:ObjectId(user_id)}

        result = self.collection_users.delete_one(queryUserCollection)

        if result.deleted_count > 0:
            self.collection_attendancy.delete_many(queryAttendancyCollection)
            print("User deleted successfully from MongoDB")
        else:
            print("User not found or not deleted")

        # Refresh the user list table after deletion
        self.list_users()



    def logout_admin(self):
        self.delete_optionFrameContent()
        self.buildFrontend_sidebar_mainPage()
     


    def add_webcam(self, label, width, height):
        self.process_webcam(label, width, height)

    def process_webcam(self, label, width, height):
        ret, frame = self.cap.read()

        if(ret):
            img_ = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgctk = ctk.CTkImage(dark_image=Image.fromarray(img_), size=(width, height))
            label.configure(image=imgctk)
            label.after(20, self.process_webcam, label, width, height)
        else:
            print("Error in reading Camera")



    def delete_mainFrameContent(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def delete_optionFrameContent(self):
        for widget in self.option_frame.winfo_children():
            widget.destroy()
    

    def hide_indicators_mainPage(self):
        self.takeAttendance_indicate.configure(bg_color='#25282e')
        self.admin_indicate.configure(bg_color='#25282e')
        self.attendancyInfo_indicate.configure(bg_color='#25282e')

    def hide_indicators_adminPage(self):
        self.add_user_indicate.configure(bg_color='#25282e')
        self.list_users_indicate.configure(bg_color='#25282e')


    def indicate(self, lb, indicators_hide, show_frame):
        indicators_hide()
        lb.configure(bg_color='#158aff')
        self.delete_mainFrameContent()
        show_frame()


    def start(self):
        self.root.mainloop()






if __name__ == "__main__":

    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(0)


    app = App()
    app.start()



