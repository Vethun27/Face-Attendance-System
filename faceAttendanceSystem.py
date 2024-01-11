
import customtkinter as ctk
import cv2
from datetime import datetime, timedelta
from PIL import Image
import face_recognition
import pymongo
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from tkcalendar import DateEntry
import hashlib
import ctypes

import constants



class App:
    def __init__(self):

        self.current_user_name = None  #  initialize the attribute name

        ctk.set_appearance_mode(constants.appApperanceMode)
        ctk.set_default_color_theme(constants.appDefaultColorTheme)
        self.root = ctk.CTk()
        self.root.geometry(constants.appGeometry + constants.appPosition)
        self.root.resizable(width=False, height=False)
        self.root.title(constants.appTitle)
        self.cap = cv2.VideoCapture(0)

        self.buildFrontend_sidebar()
        self.buildFrontend_mainFrame()
        self.takeAttendance_btn.invoke()  #starts the take Attendancy directly after App start
        
        # Connect to MongoDB
        self.client = pymongo.MongoClient(constants.mongodbHostAdress)
        self.db = self.client[constants.databaseName]
        self.collection_users = self.db[constants.userCollection]
        self.collection_attendancy = self.db[constants.attendancyCollection]
        self.collection_admins = self.db[constants.adminCollection]

        self.addAdminAccountOnce()

        self.registration_in_progress = False

    def buildFrontend_sidebar(self):
        self.option_frame = ctk.CTkFrame(self.root, fg_color='#292727', bg_color='#292727')
        self.option_frame.pack(side=ctk.LEFT)
        self.option_frame.pack_propagate(False)
        self.option_frame.configure(height=620, width=150)

        #Take Attendancy Button
        self.takeAttendance_btn = ctk.CTkButton(self.option_frame,text='Take\nAttendancy',font=('Bold', 15),fg_color='#292727',bg_color='#292727',text_color='#158aff',hover_color='#333232',corner_radius=0,border_width=0,width=150,height=35,
            command=lambda: self.indicate(self.takeAttendance_indicate, self.takeAttendance_page))

        self.takeAttendance_btn.pack(pady=20)
        self.takeAttendance_btn.configure(state="normal")
        self.takeAttendance_indicate =  ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.takeAttendance_indicate.place(x=3, y=20)

        # AttendancyInfo Button
        self.attendancyInfo_btn = ctk.CTkButton(self.option_frame, text='Info\nAttendancy', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover_color='#333232', corner_radius=0, border_width=0, width=150, height=35,
                                           command=lambda: self.indicate(self.attendancyInfo_indicate, self.attendancyInfo_page)) 
        self.attendancyInfo_btn.pack(pady=20)
        self.attendancyInfo_btn.configure(state="normal")
        self.attendancyInfo_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.attendancyInfo_indicate.place(x=3, y=100)

        # Register Button
        self.register_btn = ctk.CTkButton(self.option_frame, text='Administration', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover_color='#333232', corner_radius=0, border_width=0, width=150, height=35,
                                           command=lambda: self.indicate(self.register_indicate, self.register_page)) 
        self.register_btn.pack(pady=20)
        self.register_btn.configure(state="normal")
        self.register_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=34)
        self.register_indicate.place(x=3, y=180)


    
    def buildFrontend_mainFrame(self):
        self.main_frame = ctk.CTkFrame(self.root, border_color='black', border_width=5)
        self.main_frame.pack(side=ctk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=620, width=1100)


    


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
        
         

    def start_working(self):
        db_user_id = self.find_userID_by_picture()
        
        if db_user_id:
            db_user_name = self.find_dataObj_by_id(db_user_id, constants.nameUserAttr)
            if self.check_status_before_register_attendancy(db_user_id, "End"):
                self.register_attendancy(db_user_id, 'Start')
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
        



    def getFilteredDatesAndTime(self, userId, attendancy_table, startDate_filter, endDate_filter):
        
        self.delete_content_of_table(attendancy_table)

        start_date = datetime.strptime(startDate_filter.get(), "%d.%m.%y")
        end_date =  datetime.strptime(endDate_filter.get(), "%d.%m.%y") + timedelta(days=1)
 
        if start_date < end_date:
        
            query = {constants.userIdAttr:userId, constants.timeStampAttr:{"$gte": start_date, "$lte": end_date}}
            results = self.collection_attendancy.find(query)

            if self.collection_attendancy.count_documents(query) != 0:
                for result in results:
                    date = result[constants.timeStampAttr].strftime("%d.%m.%Y")
                    time = result[constants.timeStampAttr].strftime("%H:%M:%S")
                    dataset = (date, self.find_dataObj_by_id(userId, constants.nameUserAttr), " ", time, result[constants.statusAttr]) #self.find_dataObj_by_id(userId, constants.departmentAttr)
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

    

    def clearAttendancyCollection(self ,start_date_entry, end_date_entry):

        start_date = datetime.strptime(start_date_entry.get(), "%d.%m.%y")
        end_date =  datetime.strptime(end_date_entry.get(), "%d.%m.%y") + timedelta(days=1)

        if start_date < end_date:
            query = {constants.timeStampAttr:{"$gte": start_date, "$lte": end_date}}
            self.collection_attendancy.delete_many(query)
        else:
            CTkMessagebox(title="Error", message="Invalid Dates", icon="cancel")



    def newWindow_filterUserAttendacy(self, userId):
        filterUserAttendancy_window = ctk.CTkToplevel(self.root)
        filterUserAttendancy_window.geometry(constants.appGeometry)
        filterUserAttendancy_window.resizable(width=False, height=False)
        filterUserAttendancy_window.title(f"Attendancy Information of {self.find_dataObj_by_id(userId, constants.nameUserAttr)}")
        filterUserAttendancy_window.attributes("-topmost", True)

        filterUserAttendancy = ctk.CTkFrame(filterUserAttendancy_window)
        filterUserAttendancy.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")

        style = ttk.Style(filterUserAttendancy_window)
        style.theme_use("clam")
        style.configure("Custom1.Treeview", background="black", fieldbackground="black", foreground="white")
        attendancy_table = ttk.Treeview(filterUserAttendancy, columns=("date", "name", "department", "time","status"), show="headings",height=300, selectmode='none', style="Custom1.Treeview")
        attendancy_table.heading("date", text="Date")
        attendancy_table.heading("name", text="Name")
        attendancy_table.heading("department", text="Department")
        attendancy_table.heading("time", text="Time")
        attendancy_table.heading("status", text="Status")
        attendancy_table.pack(side=ctk.LEFT)

        sb = ttk.Scrollbar(filterUserAttendancy, orient='vertical', command=attendancy_table.yview)
        sb.pack(side="right", fill="y")
        attendancy_table.configure(yscrollcommand=sb.set)

        start_filter_label = ctk.CTkLabel(filterUserAttendancy, text="Start Date:")
        start_filter_entry = DateEntry(filterUserAttendancy, width=12, background='darkblue', foreground='black', borderwidth=2, locale='de_DE')
        end_filter_label = ctk.CTkLabel(filterUserAttendancy, text="End Date:")
        end_filter_entry = DateEntry(filterUserAttendancy, width=12, background='darkblue', foreground='black', borderwidth=2, locale='de_DE')
        start_filter_label.pack(side=ctk.TOP, pady=(30,5), padx=20)
        start_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)
        end_filter_label.pack(side=ctk.TOP, pady=(150, 5), padx=20)
        end_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)

        filter_button = ctk.CTkButton(filterUserAttendancy, text="Filter", command=lambda:self.getFilteredDatesAndTime(userId, attendancy_table, start_filter_entry, end_filter_entry), bg_color='green', fg_color='green', hover_color='#2b5c30')
        filter_button.pack(side=ctk.TOP, anchor='s', pady=(240, 0), padx=20)
    


    def delete_content_of_table(self, table):
        if(table):
            for item in table.get_children():
                table.delete(item)

 

    
    def loginUser_filterUserAttendancy(self):
        db_user_id = self.find_userID_by_picture()
        if db_user_id:
            self.newWindow_filterUserAttendacy(db_user_id)
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")
    


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


     #login function for admin
    def loginAdmin(self, userNameInput, passwordInput):
        query = {
            constants.usernameAdminAttr : userNameInput,
            constants.passwordAdminAtrr : hashlib.sha256(passwordInput).hexdigest()
        }

        adminAccount = self.collection_admins.find_one(query)

        if adminAccount:
            return True
        else:
            return False




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
        

   
    def register_page(self):
        # Entry widget to input user name
        name = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=100)
        name.pack(pady=10)

        # Button to start the registration process
        start_registration_btn = ctk.CTkButton(self.main_frame, text="Start Registration", font=('Bold', 15), bg_color='black', fg_color='white', hover_color='black', width=100, height=35, command=lambda: self.start_registration(name.get()))
        start_registration_btn.pack(pady=20)



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



    def delete_frameContent(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()

    def hide_indicators(self):
        self.takeAttendance_indicate.configure(bg_color='#25282e')
        self.register_indicate.configure(bg_color='#25282e')
        self.attendancyInfo_indicate.configure(bg_color='#25282e')
        

    def indicate(self, lb, show_frame):
        self.hide_indicators()
        lb.configure(bg_color='#158aff')
        self.delete_frameContent()
        show_frame()


    def start(self):
        self.root.mainloop()





    def start_registration(self, name):
    
        if name:
            # Set the registration state to True
            self.registration_in_progress = True
            self.current_user_name = name  # Set the current user name
            self.delete_frameContent()
         
            # Label to display the camera feed during registration
            cam_lb = ctk.CTkLabel(self.main_frame, text='')
            cam_lb.pack(side=ctk.LEFT, pady=20, padx=20)
            
            # Button to capture the user's image
            capture_btn = ctk.CTkButton(self.main_frame, text="Capture Image", bg_color='#158aff', fg_color='white', hover_color='#333232', width=100, height=35, command=lambda: self.capture_image(name))
            capture_btn.pack(pady=20)
            
            # Start the webcam feed
            self.add_webcam(cam_lb, 800, 600)
            
            # Button to finish the registration
            finish_registration_btn = ctk.CTkButton(self.main_frame, text="Finish Registration", bg_color='#158aff', fg_color='white', hover_color='#333232', width=100, height=35, command=self.finish_registration)
            finish_registration_btn.pack(pady=20)


    def finish_registration(self):
        # Reset the registration state to False
        self.registration_in_progress = False
        
        # Show a pop-up message indicating successful registration
        CTkMessagebox(title="Success", message= f"{self.current_user_name} is successfully registered in the database!", icon="check")
        
        # Go back to the login page
        self.takeAttendance_btn.invoke()

    def capture_image(self, name):
        ret, frame = self.cap.read()
        
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces in the frame using face_recognition 
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # Assuming face_locations and face_encodings are obtained from face detection
            if face_locations and face_encodings:
                # Assume the first face is the user's face
                user_face_encoding = face_encodings[0]


                user_data = {
                    constants.nameUserAttr: name,
                    constants.faceEncodingUserAttr: list(user_face_encoding),
                }
                self.collection_users.insert_one(user_data)

                print(f"User {name} registered in MongoDB!")

            else:
                print("No face detected. Please try again.")
        else:
            print("Error in reading Camera")





    




if __name__ == "__main__":

    ctypes.windll.shcore.SetProcessDpiAwareness(0)

    app = App()
    app.start()



