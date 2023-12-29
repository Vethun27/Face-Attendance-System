# face_recognition_utils.py
#test 
import cv2
import face_recognition
import os

class FaceRecognitionUtils:
    def __init__(self):
        self.video_capture = None
        self.known_face_encodings = []
        self.known_face_names = []
        self.database_folder = "Database"
        self.load_known_faces()

    def load_known_faces(self):
        for file_name in os.listdir(self.database_folder):
            if file_name.endswith(".txt"):
                path = os.path.join(self.database_folder, file_name)
                with open(path, 'r') as file:
                    lines = file.readlines()
                    encoding = [float(line.strip()) for line in lines]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(os.path.splitext(file_name)[0])

    def open_camera(self):
        self.video_capture = cv2.VideoCapture(1)

    def capture_frame(self):
        if self.video_capture is not None:
            ret, frame = self.video_capture.read()
            return ret, frame
        else:
            return False, None

    def detect_faces(self, frame):
        # Use a more accurate face detection method (HOG)
        face_locations = face_recognition.face_locations(frame, model='hog')
        return face_locations

    def encode_faces(self, frame, face_locations):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        return face_encodings

    def recognize_user(self, face_encoding):
        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
        if True in matches:
            index = matches.index(True)
            return self.known_face_names[index]
        return None

    def release_camera(self):
        if self.video_capture:
            self.video_capture.release()
