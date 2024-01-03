
import customtkinter as ctk
import cv2
from datetime import datetime
from PIL import Image
import face_recognition
import numpy as np
import pymongo
from CTkMessagebox import CTkMessagebox
from tkinter import StringVar, ttk
from tkcalendar import DateEntry

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
        self.register_btn.invoke()
        # Connect to MongoDB
        self.client = pymongo.MongoClient(constants.mongodbHostAdress)
        self.db = self.client[constants.databaseName]
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
        self.option_frame.configure(height=620, width=150)


        # Register Button
        self.register_btn = ctk.CTkButton(self.option_frame, text='Register User', font=('Bold', 15), fg_color='#292727',
                                          bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                          corner_radius=0, border_width=0, width=100, height=35,
                                          command=lambda: self.indicate(self.register_indicate, self.register_page))
        
        self.register_indicate = ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        #self.register_indicate.place(x=3, y=20)
        self.register_btn.pack(pady=20)


        # List Users Button
        self.list_users_btn = ctk.CTkButton(self.option_frame, text='List Users', font=('Bold', 15), fg_color='#292727',
                                            bg_color='#292727', text_color='#158aff', hover_color='#333232',
                                            corner_radius=0, border_width=0, width=100, height=35,
                                            command=lambda: self.indicate(self.list_users_indicate,self.list_users))
        
        self.list_users_indicate= ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.list_users_btn.pack(pady=20)


    
    def buildFrontend_mainFrame(self):
        self.main_frame = ctk.CTkFrame(self.root, border_color='black', border_width=5)
        self.main_frame.pack(side=ctk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=620, width=1100)
        


 

     

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
            capture_btn = ctk.CTkButton(self.main_frame, text="Capture Image",  fg_color='white', text_color='black', hover_color='white', width=100, height=35, command=lambda: self.capture_image(name))
            capture_btn.pack(pady=50)
            
            # Start the webcam feed
            self.add_webcam(cam_lb, 800, 600)
            



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
                }
                self.collection.insert_one(user_data)

                self.registration_in_progress = False
        
                # Show a pop-up message indicating successful registration
                CTkMessagebox(title="Success", message= f"{self.current_user_name} is successfully registered in the database!", icon="check")
        
                # Go back to the login page
                self.register_btn.invoke()

                print(f"User {name} registered in MongoDB!")


            else:
                print("No face detected. Please try again.")
        else:
            print("Error in reading Camera")


   
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




    def delete_frameContent(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()

    def hide_indicators(self):
        self.register_indicate.configure(bg_color='#25282e')
        

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



