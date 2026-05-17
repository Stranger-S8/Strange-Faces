import face_recognition
import cv2
import pickle
import os
from PIL import Image
import numpy as np

class FaceEncoding:
    ImagesPath = "data/StudentPictures"
    EncodingFile = "EncodedFile.p"

    def __init__(self):
        self.file_name = None
        self.AridNo = None
        self.img = None

    def SetEncodings(self, filename):
        self.file_name = filename
        path = os.path.join(FaceEncoding.ImagesPath, self.file_name)
        path = os.path.normpath(path)

        self.AridNo = os.path.splitext(filename)[0]

        self.img = cv2.imread(path)
        convert = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(convert)

        if not encode:
            print("No Face Was Detected")
            return None

        return encode[0]

    def StoreEncoding(self, filename):
        if not os.path.exists(FaceEncoding.EncodingFile):
            EncodingwithID = ([], [])  
        else:
            with open(FaceEncoding.EncodingFile, "rb") as file:
                EncodingwithID = pickle.load(file)

        Encoding, IDS = EncodingwithID

        encode = self.SetEncodings(filename)
        if encode is None:
            print("No encoding to store.")
            return

        Encoding.append(encode)
        IDS.append(self.AridNo)

        with open(FaceEncoding.EncodingFile, "wb") as file:
            pickle.dump((Encoding, IDS), file)

        print(f"Encoding for {filename} stored successfully.")

