appTitle = "Face Attendance System"
appGeometry = "1200x620"
appPosition = "+350+100"
appApperanceMode = "dark"
appDefaultColorTheme = "dark-blue"


#MongoDB
mongodbHostAdress = "mongodb://localhost:27017/"
databaseName = "FaceAttendanceSystem"

#collections name
adminCollection = "admins"
userCollection = "users"
attendancyCollection = "attendancy"

#Collection Attributes
idAttr = "_id"
#adminCollection
usernameAdminAttr = "username"
passwordAdminAtrr = "password"

#userCollection
nameUserAttr = "name"
faceEncodingUserAttr = "faceEncodings"
birthdateUserAttr = "birthdate"
departmentUserAttr = "departmentAttr"

#attendancyCollection
userIdAttr = "_userId"
timeStampAttr = "timestamp"
statusAttr = "status"

#Admin Account
adminUsername = "admin"
adminPassword = "admin"

#sound filepath
startWorkingSound = "resources\soundFiles\start_working.mp3"
endWorkingSound = "resources\soundFiles\end_working.mp3"

#Example Departments for Combobox
department_options = ["IT", "RH", "LOGISTICS"]

#FAQ Text (It can be extended here)
faq_text = (
                "Q: How does the face recognition attendance system work?\n"
                "A: The system uses facial recognition technology to identify employees based on unique facial features."
                "\n\nQ: Is the facial recognition system accurate?\n"
                "A: Yes, the system is designed to be highly accurate in recognizing registered employees."
                "\n\nQ: How is employee privacy protected?\n"
                "A: The system only stores facial templates, not actual images, ensuring employee privacy."
                "\n\nQ: What happens if an employee's face changes (e.g., due to a beard or glasses)?\n"
                "A: The system is adaptable and can be retrained to accommodate such changes."
            )

#Path to the video staring from the current file (faceAttendanceSystem.py)
video_filePath = "./resources/tutVideo/tutVideo.mp4"