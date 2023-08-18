import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-43a00-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "20104316":
        {
            "name": "Vishnuvardhan M",
            "Department": "Computer Science",
            "Year": "2021-2024",
            "Last Attendance Time": "2023-08-16 00:54:34",
            "total_attendance": 106
        },
    "20104170":
        {
            "name": "YADAM KARTHIK",
            "Department": "Computer Science",
            "Year": "20224-2024",
            "Last Attendance Time": "2023-08-16 00:57:34",
            "total_attendance": 37
        },
    "20104122":
        {
            "name": "SAI SURAJ SHANKER",
            "Department": "Computer Science",
            "Year": "2020-2024",
            "Last Attendance Time": "2023-08-16 00:58:34",
            "total_attendance": 45
        },
    "20104133":
        {
            "name": "Elon Musk",
            "Department": "Computer Science",
            "Year": "2020-2024",
            "Last Attendance Time": "2023-08-16 00:58:34",
            "total_attendance": 1
        }
}

for key, value in data.items():
    ref.child(key).set(value)
