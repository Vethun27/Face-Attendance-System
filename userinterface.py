
import customtkinter as ctk
import cv2
from datetime import datetime
from PIL import Image
import face_recognition
import numpy as np
import pymongo
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
from tkcalendar import DateEntry

import constants



#TODO: If we send the time for start or end working, we should fetch which time is already registered (end or start)
#       based on that the user can register his start or end working
#       if e.g. the start time is the last the element o that user, it should be prevented that the user can register another start time ->  according to that there will be messagebox



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
        self.collection = self.db["users"]

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

        # AttendanyInfo Button
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
        


    def start_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("Start Working... Time: " + formatted_timestamp)

        db_user_name = self.find_verified_user()
        
        if db_user_name:
            CTkMessagebox(title="Welcome", message=f"Welcome to work, {db_user_name}!")
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")


    
    def end_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("End Working... Time: " + formatted_timestamp)

        db_user_name = self.find_verified_user()

        if db_user_name:
            CTkMessagebox(title="Goodbye", message=f"Goodbye, {db_user_name}!")
        else:
            CTkMessagebox(title="Error", message="No matching user found", icon="cancel")

     
    

    def find_verified_user(self):
        # Capture a frame from the camera
        ret, frame = self.cap.read()

        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces in the frame using face_recognition library
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # Assuming face_locations and face_encodings are obtained from face detection
            if face_locations and face_encodings:
                # Assume the first face is the user's face
                user_face_encoding = face_encodings[0]

                # Fetch all users from the MongoDB collection
                all_users = self.collection.find()

                for user in all_users:
                    # Get the user's name and face encoding from the database
                    db_user_name = user["name"]
                    db_face_encoding = np.array(user["numfeature"])

                    # Compare the face encodings
                    match = face_recognition.compare_faces([db_face_encoding], user_face_encoding)

                    if any(match):
                        # At least one matching face found
                        return db_user_name
                    else:
                        # No matching face found
                        return None
            else:
                return None


    


    def start_registration(self, name):
    
        if name:
            # Set the registration state to True
            self.registration_in_progress = True
            self.current_user_name = name  # Set the current user name
            self.delete_frameContent()
         
            # Label to display the camera feed during registration
            cam_lb = ctk.CTkLabel(self.main_frame, text='', pady=20, padx=20)
            cam_lb.pack(side=ctk.LEFT)
            
            # Button to capture the user's image
            capture_btn = ctk.CTkButton(self.main_frame, text="Capture Image", bg_color='#158aff', fg_color='white', hover_color='#333232', width=100, height=35, command=lambda: self.capture_image(name))
            capture_btn.pack(pady=20)
            

            #put condition to dont let known face register w/ different names 



            # Start the webcam feed
            self.add_webcam(cam_lb, 800, 520)
            
            

    def finish_registration(self):
        # Reset the registration state to False
        self.registration_in_progress = False
        
        # Show a pop-up message indicating successful registration
        CTkMessagebox(title="Success", message= f"{self.current_user_name} is successfully registered in the database!", icon="check")
        
        # Go back to the login page
        self.takeAttendance_btn.invoke()

    def capture_image(self, name):
        ret, frame = self.cap.read()
        

        db_user_name = self.find_verified_user()
        if db_user_name:
            CTkMessagebox(title="Error, please try again", message=f"This face already exists with the name , {db_user_name}!")
            self.register_page()
          
        else:
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
                        "name": name,
                        "numfeature": list(user_face_encoding),
                        # Add other relevant data fields
                    }
                    self.collection.insert_one(user_data)

                    print(f"User {name} registered in MongoDB!")

                    # Button to finish the registration
                    finish_registration_btn = ctk.CTkButton(self.main_frame, text="Finish Registration", bg_color='#158aff', fg_color='white', hover_color='#333232', width=100, height=35, command=self.finish_registration)
                    finish_registration_btn.pack(pady=20)

                else:
                    print("No face detected. Please try again.")
            else:
                print("Error in reading Camera")



    def getFilteredDatesAndTIme(self):
        #TODO
        print("Fetch Dates and Time from database")



    def newWindow_filterUserAttendacy(self, userName):
        filterUserAttendancy_window = ctk.CTkToplevel(self.root)
        filterUserAttendancy_window.geometry(constants.appGeometry)
        filterUserAttendancy_window.resizable(width=False, height=False)
        filterUserAttendancy_window.title(f"Attendancy Information of {userName}")
        filterUserAttendancy_window.attributes("-topmost", True)

        filterUserAttendancy = ctk.CTkFrame(filterUserAttendancy_window)
        filterUserAttendancy.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")

        style = ttk.Style(filterUserAttendancy_window)
        style.theme_use("winnative")
        style.configure("Treeview", background="black", fieldbackground="black", foreground="white")
        self.table = ttk.Treeview(filterUserAttendancy, columns=("date", "name", "department", "time","attendance"), show="headings",height=300)
        self.table.heading("date", text="Date")
        self.table.heading("name", text="Name")
        self.table.heading("department", text="Department")
        self.table.heading("time", text="Time")
        self.table.heading("attendance", text="Start/End")
        self.table.pack(side=ctk.LEFT)

        start_filter_label = ctk.CTkLabel(filterUserAttendancy, text="Start Date:")
        start_filter_entry = DateEntry(filterUserAttendancy, width=12, background='darkblue', foreground='black', borderwidth=2, locale='de_DE')
        end_filter_label = ctk.CTkLabel(filterUserAttendancy, text="End Date:")
        end_filter_entry = DateEntry(filterUserAttendancy, width=12, background='darkblue', foreground='black', borderwidth=2, locale='de_DE')
        start_filter_label.pack(side=ctk.TOP, pady=(30,5), padx=20)
        start_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)
        end_filter_label.pack(side=ctk.TOP, pady=(150, 5), padx=20)
        end_filter_entry.pack(side=ctk.TOP, pady=0, padx=20)

        filter_button = ctk.CTkButton(filterUserAttendancy, text="Filter", command=self.getFilteredDatesAndTIme, bg_color='green', fg_color='green', hover_color='#2b5c30')
        filter_button.pack(side=ctk.TOP, anchor='s', pady=(240, 0), padx=20)

        


        
    
    def loginUser_filterUserAttendancy(self):
        db_user_name = self.find_verified_user()
        if db_user_name:
            self.newWindow_filterUserAttendacy(db_user_name)
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




if __name__ == "__main__":
    app = App()
    app.start()



