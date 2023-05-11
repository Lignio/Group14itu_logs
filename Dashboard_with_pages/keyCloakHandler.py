from keycloak import KeycloakOpenID, keycloak_admin,KeycloakAdmin

#--- Currently logged in user ---#
CurrentUser = None
# This field is the one that acts as the active user session. The pages  does and should interact
# with this field only through the currentUserSession class, as the field is set to an instance of that class when you log in.
#--------------------------------#

# Initializes the keycloak client I think. Used to interact with keycloak most places
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                client_id="dashclient",
                                realm_name="master",
                                client_secret_key="woo797pz61dd17nZxWTWQfMygWLY4DJB")

# Initializes the keycloak admin client, used to get access to user groups and permissions
admin = KeycloakAdmin(server_url='http://localhost:8080/',
                      username='admin',
                      password='admin',
                      realm_name='master',
                      verify=True)

# Gets authentication token for user, used to gain access to user information based on login info
def getAuthTokenForUser(username, userPass):
    
    token = keycloak_openid.token(username, userPass)['access_token']
    return token

# Get user info returns only the basic info on the user, such as their username and email. 
# This function is not in use right now, but is there if we need it going forward.
def getUserInfo(username,userPass):
    token = getAuthTokenForUser(username,userPass)
    return keycloak_openid.userinfo(token)

# Admin client is used to gain access to a users groups and roles. Is done with user_id, not username.
# Example userID: 47c7a85c-0764-4a20-bbf6-ba7fe2860e26
# UserID is available to see in the keycloak admin console, but is also returned with userinfo as in
# getAuthTokenForUser
# This function is not in use right now, but is there if we need it going forward.
def getUserGroupsAndRoles(userID):
    return admin.get_user_groups(user_id=userID)

# This class handles any active user session. The token is never interacted with outside the class, and
# should not be.
class currentUserSession():
    def __init__(self, userName, userPass):
        self.__token = getAuthTokenForUser(userName, userPass)
        self.username = userName

    def getInfo(self):
        return keycloak_openid.userinfo(self.__token)

    def __str__(self):
        return "Currently logged in user: {}".format(self.username)

    def logout(self):
        self.__token = None

    def isLoggedIn(self):
        return False if self.__token is None else True
