
from faceRecognitionUtils import faceRecognitionUtils
import constants


class userInformationsFromDb:
    def __init__(self, database):

        if database == None:
            print("No connection to Database")
            return None
        
        #private variables
        self._faceRecognitionUtils = faceRecognitionUtils()

        self._idAttr = constants.idAttr
        self._encodingsAttr = constants.faceEncodingAttr
        self._birthdateAttr = constants.birthdateAttr
        self._departmentAttr = constants.departmentAttr

        #public variables
        self.collection_users = database[constants.userCollection]
        
    

    def find_userID_by_picture(self, frame):
        
        if frame:
            faceEncodingOfFrame = self._faceRecognitionUtils.getFaceEncodingsOfFrame(frame)

            if faceEncodingOfFrame:

                all_users = self.collection_users.find()

                for user in all_users:
                    db_user_id = user[self._idAttr]
                    db_face_encoding = user[self._encodingsAttr]

                    match = self._faceRecognitionUtils.compareFaces(db_face_encoding, faceEncodingOfFrame)

                    if match:
                        # At least one matching face found
                        return db_user_id
        return None
    

    def _find_dataObj_by_id(self, _userId, dataAttr):

        if _userId and dataAttr:
            query = {constants.userIdAttr: _userId}

            user = self.collection_users.find_one(query)

            if user:
                if user[dataAttr]:
                    return user[dataAttr]
          
        return None


    def find_name_by_id(self, userId):
        return self._find_dataObj_by_id(userId, constants.nameAttr)

    def find_birthdate_by_id(self, userId):
        return self._find_dataObj_by_id(userId, constants.birthdateAttr)

    def find_department_by_id(self, userId):
        return self._find_dataObj_by_id(userId, constants.departmentAttr)

