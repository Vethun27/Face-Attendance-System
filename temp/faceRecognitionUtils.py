
import cv2
import face_recognition

class faceRecognitionUtils:
    def __init__(self):
        pass


    def getFaceEncodingsOfFrame(self, frame):

        if frame:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            return face_encodings[0]

        return None
            

    def compareFaces(self, knowsFaceEncoding, faceEncodingToCheck):

        if knowsFaceEncoding and faceEncodingToCheck:

            match = face_recognition.compare_faces([knowsFaceEncoding], faceEncodingToCheck)

            if any(match):
                return True
        
        return False
