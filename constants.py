appTitle = "Face Attendance System"
appGeometry = "1200x620"
appPosition = "+350+100"
appApperanceMode = "dark"
appDefaultColorTheme = "dark-blue"


#MongoDB
mongodbHostAdress = "mongodb://localhost:27017/FaceRecognitionApp"
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