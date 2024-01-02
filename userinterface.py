from tkinter import Tk, TkVersion, messagebox, ttk, StringVar, Entry
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import constants
from face_recognition_utils import FaceRecognitionUtils
import os
from PIL import Image, ImageTk
import face_recognition
import numpy as np
from tkcalendar import DateEntry 
import pymongo





class App:
    def __init__(self):

        self.current_user_name = None  #  initialize the attribute name
        self.logged_in = False
        self.admin_logged_in = False  # Keep track of admin login status




        ctk.set_appearance_mode(constants.appApperanceMode)
        ctk.set_default_color_theme(constants.appDefaultColorTheme)
        self.root = ctk.CTk()
        self.root.geometry(constants.appGeometry + constants.appPosition)
        self.root.resizable(width=False, height=False)
        self.root.title(constants.appTitle)
        self.loggedIn = False
        self.cap = cv2.VideoCapture(0)

        self.buildFrontend_sidebar()
        self.buildFrontend_mainFrame()
        self.takeAttendance_btn.invoke()  #starts the take Attendancy directly after App start
        
        # Connect to MongoDB
        self.client = pymongo.MongoClient("mongodb://localhost:27017/FaceRecognitionApp")
        self.db = self.client["FaceRecognitionApp"]
        self.collection = self.db["users"]

        self.registration_in_progress = False


    def validate_date(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
        if text in '0123456789-':  # Allow only digits, dot, slash, and hyphen
            parts = value_if_allowed.split('-')
            if len(parts) == 1:
                if len(parts[0]) > 2:
                    return False
                if len(parts[0]) == 2 and action != 'delete':
                    value_if_allowed += '-'
            elif len(parts) == 2:
                if len(parts[0]) > 2 or len(parts[1]) > 2:
                    return False
                if len(parts[1]) == 2 and action != 'delete':
                    value_if_allowed += '-'
            elif len(parts) == 3:
                if len(parts[0]) > 2 or len(parts[1]) > 2 or len(parts[2]) > 4:
                    return False
            return True
        else:
            return False

    def buildFrontend_sidebar(self):
        self.option_frame = ctk.CTkFrame(self.root, fg_color='#292727', bg_color='#292727')
        self.option_frame.pack(side=ctk.LEFT)
        self.option_frame.pack_propagate(False)
        self.option_frame.configure(height=620, width=100)

        self.takeAttendance_btn = ctk.CTkButton(self.option_frame, text='Take\nAttendancy', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover_color='#333232', corner_radius=0, border_width=0, width=100, height=35,
                                               command=lambda: self.indicate(self.takeAttendance_indicate, self.takeAttendance_page))

        self.takeAttendance_btn.pack(pady=20)
        self.takeAttendance_btn.configure(state="normal")
        self.takeAttendance_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        #self.takeAttendance_indicate.place(x=0, y=0)

       
        self.admin_btn = ctk.CTkButton(self.option_frame, text='Admin', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover_color='#333232', corner_radius=0, border_width=0, width=100, height=35, state="normal",
                                           command=lambda: self.indicate(self.admin_indicate, self.admin_page))
        self.admin_btn.pack(pady=20)
        self.admin_btn.configure(state="normal")
        self.admin_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        #self.admin_indicate.place(x=0, y=0)

       

        # Add the "Register User" button (initially disabled)
        self.register_btn = ctk.CTkButton(self.option_frame, text='Register User', font=('Bold', 15), fg_color='#292727',
                                          bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                          corner_radius=0, border_width=0, width=100, height=35,
                                          command=lambda: self.indicate(self.register_indicate, self.register_page))
        
        self.register_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        #self.register_indicate.place(x=3, y=20)
        self.register_btn.pack(pady=20)
        self.register_btn.pack_forget()  # Set initial state to "hidden"

        # Add the "List Users" button (initially disabled)
        self.list_users_btn = ctk.CTkButton(self.option_frame, text='List Users', font=('Bold', 15), fg_color='#292727',
                                            bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                            corner_radius=0, border_width=0, width=100, height=35,
                                            command=lambda: self.indicate(self.list_users_indicate,self.list_users))
        
        self.list_users_indicate= ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.list_users_btn.pack(pady=20)
        self.list_users_btn.pack_forget()  # Set initial state to "hidden"

        # Add the "List Users" button (initially disabled)
        self.logout_admin_btn = ctk.CTkButton(self.option_frame, text='Back to main', font=('Bold', 15), fg_color='#292727',
                                            bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                            corner_radius=0, border_width=0, width=100, height=35,
                                            command=lambda : self.indicate(self.logout_admin_indicate,self.logout_admin))
        
        self.logout_admin_indicate= ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.logout_admin_btn.pack(pady=20)
        self.logout_admin_btn.pack_forget()  # Set initial state to "hidden"
        


    def buildFrontend_mainFrame(self):
        self.main_frame = ctk.CTkFrame(self.root, border_color='black', border_width=5)
        self.main_frame.pack(side=ctk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=620, width=1100)
        

    def delete_frameContent(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()

    def hide_indicators(self):
        self.takeAttendance_indicate.configure(bg_color='#c3c3c3')
        

    def indicate(self, lb, page):
        self.hide_indicators()
        lb.configure(bg_color='#158aff')
        self.delete_frameContent()
        page()


    def admin_page(self):


        instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Admin credentials", font=('Bold', 20), text_color='white')
        instruction_label.pack(pady=(100, 10), padx=10)  # Adjust the pady value to add more space at the top

        adminname = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=100)
        adminname.pack(pady=10)
        adminpw = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=100, show='*')
        adminpw.pack(pady=10)
        login_btn = ctk.CTkButton(self.main_frame, text="Login", font=('Bold', 15), fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.login_admin(adminname.get(),adminpw.get()))
        login_btn.pack(pady=20)

    def login_admin(self,adminname,adminpw):
        admin_username = "admin"  #  admin username
        admin_password = "admin"  #  admin password
        if adminname == admin_username and adminpw == admin_password:
            messagebox.showinfo("Success", "Admin login successful!")

            # Enable buttons for admin functionalities
            self.admin_logged_in = True
            self.enable_admin_buttons()
            # show directly the register button 
            self.register_btn.invoke()

        else:
            messagebox.showerror("Error", "Invalid admin credentials!")

    def enable_admin_buttons(self):
        # Check if the admin is logged in before enabling buttons
        if self.admin_logged_in:
            # Enable the buttons for admin functionalities
            self.register_btn.pack(pady=20)
            self.list_users_btn.pack(pady=20)
            self.takeAttendance_btn.pack_forget()
            self.admin_btn.pack_forget()
            self.logout_admin_btn.pack(pady=20)



    def logout_admin(self):

        self.takeAttendance_btn.invoke() 

        # Reset the admin login status
        self.admin_logged_in = False

        # Hide the buttons for admin functionalities
        self.register_btn.pack_forget()
        self.list_users_btn.pack_forget()
        self.takeAttendance_btn.pack(pady=20)
        self.admin_btn.pack(pady=20)
        self.logout_admin_btn.pack_forget()

    def start_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("Start Working... Time: " + formatted_timestamp)

        # Check if a user is already logged in
        if self.current_user_name:
            messagebox.showinfo("Error", f"{self.current_user_name} is already logged in.")
            return

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
                        self.current_user_name = db_user_name
                        messagebox.showinfo("Welcome", f"Welcome to work, {db_user_name}!")
                        break  # Break out of the loop once a match is found
                else:
                    # No matching face found
                    messagebox.showinfo("Error", "No matching user found. Access denied.")

            else:
                print("No face detected. Please try again.")
        else:
            print("Error in reading Camera")


    def match_user(self, face_encoding):
        # Iterate through users in the database mongo db and check for a match
        for user in self.collection.find():
            known_face_encoding = user["numfeature"]
            # Compare the face encoding in mongo db with the known face
            match = face_recognition.compare_faces([known_face_encoding], face_encoding)

            if match[0]:
                return user

        return None
    
    def end_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("End Working... Time: " + formatted_timestamp)

        # Check if a user is logged in
        if self.current_user_name:
            messagebox.showinfo("Goodbye", f"Goodbye, {self.current_user_name}!")
            self.current_user_name = None
        else:
            messagebox.showinfo("Error", "No user is currently logged in.")

    def takeAttendance_page(self):
        if not self.logged_in:
            self.takeAttendace_frame = ctk.CTkFrame(self.main_frame)
            self.takeAttendace_frame.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")
            cam_lb = ctk.CTkLabel(self.takeAttendace_frame, text='')
            cam_lb.pack(side=ctk.LEFT)
            self.add_webcam(cam_lb)

            start_work_btn = ctk.CTkButton(self.takeAttendace_frame, text="Start Work", bg_color='green', fg_color='green', hover_color='#2b5c30', width=500, height=260, command=self.start_working)
            start_work_btn.pack(side=ctk.TOP, pady=15, padx=20)

            end_work_btn = ctk.CTkButton(self.takeAttendace_frame, text="End Work", bg_color='red', hover_color='#5c1d1d', fg_color='red', width=500, height=260, command=self.end_working)
            end_work_btn.pack(side=ctk.TOP, anchor='s', pady=15, padx=20)
        else:
            messagebox.showinfo("Error", "You are already logged in.")


   
    def register_page(self):
        self.delete_frameContent()

        # Label to instruct the user
        instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Employee name", font=('Bold', 15), text_color='white')
        instruction_label.pack(pady=(50, 10), padx=10)  # Adjust the pady value to add more space at the top

        
        # Entry widget to input user name
        name = ctk.CTkEntry(self.main_frame, font=('Bold', 15), width=200)
        name.pack(pady=10)

        # Label for birthdate instruction
        birthdate_instruction_label = ctk.CTkLabel(self.main_frame, text="Please Enter the Birthdate (DD-MM-YYYY)",font=('Bold', 15), text_color='white')
        birthdate_instruction_label.pack(pady=10)

        # StringVar to store the validated date
        validated_date = StringVar()

        # Validate function for the Entry widget
        validate_date_func = self.root.register(self.validate_date)

        # Entry widget for birthdate input
        birthdate = ctk.CTkEntry(self.main_frame, font=('Bold', 15), textvariable=validated_date, validate='key', validatecommand=(validate_date_func, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'))
        birthdate.pack(pady=10)
        # Button to start the registration process
        start_registration_btn = ctk.CTkButton(self.main_frame, text="Start Registration", font=('Bold', 15), fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.start_registration(name.get()))
        start_registration_btn.pack(pady=20)

    def start_registration(self, name):
    
        if name:
            # Set the registration state to True
            self.registration_in_progress = True
            self.current_user_name = name  # Set the current user name
            self.delete_frameContent()
         
            # Label to display the camera feed during registration
            cam_lb = ctk.CTkLabel(self.main_frame, text='')
            cam_lb.pack(side=ctk.LEFT)
            
            # Button to capture the user's image
            capture_btn = ctk.CTkButton(self.main_frame, text="Capture Image",  fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.capture_image(name))
            capture_btn.pack(pady=20)
            
            # Start the webcam feed
            self.add_webcam(cam_lb)
    


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
                    "name": name,
                    "numfeature": list(user_face_encoding),
                    # Add other relevant data fields
                }
                self.collection.insert_one(user_data)

                        # Reset the registration state to False
                self.registration_in_progress = False
        
        # Show a pop-up message indicating successful registration
                messagebox.showinfo("Success", f"{self.current_user_name} is successfully registered in the database!")

        # Go back to the register page
                self.register_btn.invoke()

                print(f"User {name} registered in MongoDB!")

            else:
                print("No face detected. Please try again.")
        else:
            print("Error in reading Camera")



    


    def list_users(self):
        self.delete_frameContent()

        # Fetch all users from the MongoDB collection
        all_users = self.collection.find()

        # Create table within the same window
        self.user_list_table = ttk.Treeview(self.main_frame, columns=("User ID", "User Name", "Actions"), show="headings", height=40)

        # Style for the Treeview widget
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Bold', 12))
        style.configure("Treeview", font=('Arial', 10))

        self.user_list_table.heading("User ID", text="User ID")
        self.user_list_table.heading("User Name", text="User Name")
        self.user_list_table.heading("Actions", text="Actions")

        self.user_list_table.column("User ID", minwidth=50, width=200)
        self.user_list_table.column("User Name", minwidth=100, width=800)
        self.user_list_table.column("Actions", minwidth=50, width=200)

        # Set a custom cell renderer for the "Actions" column
        self.user_list_table.heading("Actions", text="Actions", command=lambda: None)  # This line is necessary for the custom renderer to work
        self.user_list_table.bind("<Button-1>", self.on_tree_click)  # Bind the click event to the custom renderer

        # Add user data to the table
        for index, user in enumerate(all_users, start=1):
            delete_button = ttk.Button(self.user_list_table, text="Delete", command=lambda u=user: self.delete_user(u["_id"]))
            self.user_list_table.insert("", "end", values=(index, user["name"], delete_button))

        self.user_list_table.pack(pady=20, padx=20)

    def on_tree_click(self, event):
        item = self.user_list_table.selection()[0]
        column = self.user_list_table.identify_column(event.x)
        if column == "#3":  # Check if the clicked column is the "Actions" column
            user_id = self.user_list_table.item(item, "values")[0]
            self.delete_user(user_id)

    def delete_user(self, user_id):
        # Remove the user from the MongoDB collection
        self.collection.delete_one({"_id": user_id})

        # Remove the user from the table
        selected_item = self.user_list_table.selection()[0]
        self.user_list_table.delete(selected_item)

        
    def add_webcam(self, label):
        self.process_webcam(label)

    def process_webcam(self, label):
        ret, frame = self.cap.read()

        if(ret):
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            imgctk = ctk.CTkImage(dark_image=Image.fromarray(img_), size=(800, 620))
            label.configure(image=imgctk)
            label.after(20, self.process_webcam, label)
        else:
            print("Error in reading Camera")

    def start(self):
        self.root.mainloop()




if __name__ == "__main__":
    app = App()
    app.start()



