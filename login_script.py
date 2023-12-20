# login_script.py
import numpy as np
from face_recognition_utils import FaceRecognitionUtils
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import face_recognition
from pymongo import MongoClient


class LoginScript:
    def __init__(self, root, show_main_menu_callback):
        self.face_recognition_utils = FaceRecognitionUtils()
        self.root = root
        self.show_main_menu_callback = show_main_menu_callback
        
        # Connect to MongoDB
        self.client = MongoClient("mongodb://localhost:27017/FaceRecognitionApp")
        self.db = self.client["FaceRecognitionApp"]
        self.collection = self.db["users"]


    def run(self):
        self.root.title("Login")

        canvas = tk.Canvas(self.root, width=640, height=480)
        canvas.pack(pady=10)

        # Open the camera
        self.face_recognition_utils.open_camera()

        # Call the show_frame_login method to display the camera feed for login
        self.show_frame_login(canvas)

        # Bind the closing event to release the camera
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def show_frame_login(self, canvas):
        ret, frame = self.face_recognition_utils.capture_frame()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Recognize faces in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matched_name = self.recognize_user_from_db(face_encoding)
                if matched_name:
                    # Display a popup for the recognized user
                    messagebox.showinfo("Welcome", f"Welcome, {matched_name}!")
                    
                else:
                    messagebox.showinfo("User not in the database!")
                    

            # Display the frame
            photo = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
            canvas.config(width=photo.width(), height=photo.height())
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo

            # Call the show_frame_login method after 10 milliseconds
            self.root.after(10, lambda: self.show_frame_login(canvas))

    def recognize_user_from_db(self, recognized_face_encoding):
        # Retrieve face encodings from MongoDB
        user_data = self.collection.find_one()  # You might need to specify a query here

        if user_data and "numfeature" in user_data:
            # Parse the string to get a list of float values
            stored_face_encoding_str = user_data["numfeature"]
            
            try:
                stored_face_encoding_list = [float(val) for val in stored_face_encoding_str if val != '-']
            except ValueError:
                # Handle the case where conversion to float fails
                return None

            # Convert the list to a NumPy array
            stored_face_encoding = np.array(stored_face_encoding_list).astype(np.float64)
            recognized_face_encoding = recognized_face_encoding.astype(np.float64)

            # Compare the recognized face encoding with stored face encoding
            match = face_recognition.compare_faces([stored_face_encoding], recognized_face_encoding)

            if match[0]:
                return user_data.get("name", None)

        return None

    def on_closing(self):
        # Release the camera when the window is closed
        self.face_recognition_utils.release_camera()
        self.root.destroy()

if __name__ == "__main__":
    login_script = LoginScript()
    login_script.run()