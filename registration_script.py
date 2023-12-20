# registration_script.py
from face_recognition_utils import FaceRecognitionUtils
import cv2
from PIL import Image, ImageTk
import tkinter as tk
import os
from pymongo import MongoClient  # Import MongoClient from pymongo


class RegistrationScript:
    def __init__(self, root, show_main_menu_callback):
        self.face_recognition_utils = FaceRecognitionUtils()
        self.root = root
        self.show_main_menu_callback = show_main_menu_callback
        # Connect to MongoDB
        self.client = MongoClient("mongodb://localhost:27017/FaceRecognitionApp")
        self.db = self.client["FaceRecognitionApp"]
        self.collection = self.db["users"]

    def run(self):
        self.root.title("Registration")

        label = tk.Label(self.root, text="Automatic Face Registration")
        label.pack(pady=10)

        # Entry for the user's name
        self.name_entry = tk.Entry(self.root, width=30)
        self.name_entry.pack(pady=10)

        # Register button
        register_button = tk.Button(self.root, text="Start Registration", command=self.start_registration)
        register_button.pack(pady=10)

        # Canvas for displaying the camera feed
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.pack(pady=10)

        # Open the camera
        self.face_recognition_utils.open_camera()

        # Bind the closing event to release the camera
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def start_registration(self):
        # Get the user-provided name from the entry widget
        name = self.name_entry.get().strip()

        if name:
            # Call the show_frame_registration method to display the camera feed for registration
            self.show_frame_registration(name)

    def show_frame_registration(self, name):
        ret, frame = self.face_recognition_utils.capture_frame()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces in the frame
            face_locations = self.face_recognition_utils.detect_faces(rgb_frame)
            face_encodings = self.face_recognition_utils.encode_faces(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Automatically register the face with the user-provided name
                self.register_user(name, face_encoding)

            # Display the camera video
            photo = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

            # Call the show_frame_registration method after 10 milliseconds
            self.root.after(10, lambda: self.show_frame_registration(name))

    def register_user(self, name, face_encoding):
        if name:
            self.face_recognition_utils.known_face_encodings.append(face_encoding)
            self.face_recognition_utils.known_face_names.append(name)

            # Save the user's encoding to a file in the database folder
            user_file_path = os.path.join(self.face_recognition_utils.database_folder, f"{name}.txt")
            with open(user_file_path, 'w') as file:
                for val in face_encoding:
                    file.write(f"{val}\n")

            print(f"User {name} automatically registered!")
            user_data = {
            "name": name,
            "numfeature": list(face_encoding),
            # Add other relevant data fields
        }
            self.collection.insert_one(user_data)

            print(f"User {name} registered in MongoDB!")


    def on_closing(self):
        self.face_recognition_utils.release_camera()
        self.root.destroy()


if __name__ == "__main__":
    registration_script = RegistrationScript()
    registration_script.run()
