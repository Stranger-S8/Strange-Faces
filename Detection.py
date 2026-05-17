import cv2
import face_recognition
import pickle
import numpy as np


class DetectFace:

    def __init__(self):
        
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 370)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 370)

        self.detected_id=None

        try:
            with open("EncodedFile.p", "rb") as file:
                self.encodeList = pickle.load(file)

                self.encodings, self.ids = self.encodeList
        except FileNotFoundError:
             print("File Not Found")

    def CompareFace(self):
            success, img = self.cam.read()
            
            if not success:
                print("Failed to capture image.")
                return None

            imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for encodeFace, locFace in zip(encodeCurFrame, faceCurFrame):
    
                matches = face_recognition.compare_faces(self.encodings, encodeFace)
                faceDis = face_recognition.face_distance(self.encodings, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    top, right, bottom, left = [coord * 4 for coord in locFace]

                    cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

                    cv2.putText(img, self.ids[matchIndex], (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    self.getAridNo(self.ids[matchIndex])

                    print(f"Match: {self.ids[matchIndex]} | Face Distance: {faceDis[matchIndex]}")
            
            return img
    
    def getAridNo(self,aridNo):
         self.detected_id=aridNo

    def releaseResources(self):
        self.cam.release()
        cv2.destroyAllWindows()



