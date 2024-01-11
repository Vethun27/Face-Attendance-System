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
usernameAttr = "username"
passwordAtrr = "password"

#userCollection
nameAttr = "name"
faceEncodingAttr = "faceEncodings"
birthdateAttr = "birthdate"
departmentAttr = "departmentAttr"

#attendancyCollection
userIdAttr = "_userId"
dateAttr = "date"
timeAttr = "time"
statusAttr = "status"