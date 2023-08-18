import datetime
import os
import pickle
import time

import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import sys

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-43a00-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-43a00.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/ATTENDANCE.png')

# mode Images

folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load Encode File
print("Encode File Loading")
file = open("EncodeFile.p", 'rb')
encodelistKnownwithids = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodelistKnownwithids
print("Encode File Loaded")
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgs = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    facecurframe = face_recognition.face_locations(imgs)
    encodecurframe = face_recognition.face_encodings(imgs, facecurframe)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeface, faceloca in zip(encodecurframe, facecurframe):
        matches = face_recognition.compare_faces(encodeListKnown, encodeface)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeface)
        # print("matches", matches)
        print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("Match Index",matchIndex)

        if matches[matchIndex]:
            # print("known Face Detected")
            print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceloca
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1
    if counter != 0:
        if counter == 1:
            # get the Data
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)
            # image get

            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            # update
            datetimeObject = datetime.strptime(studentInfo['Last Attendance Time'],
                                               "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed > 30:
                ref = db.reference(f'Students/{id}')
                studentInfo['total_attendance'] += 1
                ref.child('total_attendance').set(studentInfo['total_attendance'])
                ref.child('Last Attendance Time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                modeType = 3
                counter = 0
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if modeType != 3:

            if 10 < counter < 20:
                modeType = 2
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter <= 10:
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
                cv2.putText(imgBackground, str(studentInfo['Department']), (1004, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
                cv2.putText(imgBackground, str(studentInfo['Year']), (11250, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                cv2.putText(imgBackground, str(studentInfo['name']), (815, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
        counter += 1

    if counter >= 20:
        counter = 0
        modType = 0
        studentInfo = []
        imgStudent = []
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # background merge
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)


    def terminate(q):
        if q.name == 'q':
            print("program ended")
            sys.exit()
