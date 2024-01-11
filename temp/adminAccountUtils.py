import hashlib
import constants

class adminAccount:
    def __init__(self, database):
        
        if database == None:
            print("No connection to Database")
            return None
        
        #private variables
        self._collection_adminAccounts = database[constants.adminCollection]
        self._usernameAttr = constants.usernameAttr
        self._passwordAtrr = constants.passwordAtrr
        
        self.addOneAdminAccountOnce("admin", "admin")



    # possiblity to create admin accounts 
    def createAdminAccount(self, username, password):
        
        adminAccData = {
            self._usernameAttr : username,
            self._passwordAtrr : hashlib.sha256(password.encode()).hexdigest()
        }
        self._collection_adminAccounts.insert_one(adminAccData)



    #Adding Admin Account with username "admin" and password "admin" once
    def addOneAdminAccountOnce(self, username_admin, password_admin):
        query = {self._usernameAttr : username_admin}
        db_username_admin = self._collection_adminAccounts.find_one(query)
        if db_username_admin != None:
            self.createAdminAccount(username_admin, password_admin)



    
    #login function for admin
    def loginAdmin(self, userNameInput, passwordInput):
        query = {
            self._usernameAttr : userNameInput,
            self._passwordAtrr : hashlib.sha256(passwordInput).hexdigest()
        }

        adminAccount = self._collection_adminAccounts.find_one(query)

        if adminAccount:
            return True
        else:
            return False
    