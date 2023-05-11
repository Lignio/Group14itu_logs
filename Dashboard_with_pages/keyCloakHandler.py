from keycloak import KeycloakOpenID, keycloak_admin,KeycloakAdmin

#--- Currently logged in user ---#
CurrentUser = None
# This field is the one that acts as the active user session. The pages  does and should interact
# with this field only through the currentUserSession class, as the field is set to an instance of that class when you log in.
#--------------------------------#

# Initializes the keycloak client I think. Used to interact with keycloak most places
keycloak_openid = KeycloakOpenID(server_url="http://keycloak:8080/",
                                client_id="dashclient",
                                realm_name="master",
                                client_secret_key="woo797pz61dd17nZxWTWQfMygWLY4DJB")


# Gets authentication token for user, used to gain access to user information based on login info
def getAuthTokenForUser(username, userPass):
    
    token = keycloak_openid.token(username, userPass)['access_token']
    return token

# Get user info returns only the basic info on the user, such as their username and email. 
# This function is not in use right now, but is there if we need it going forward.
def getUserInfo(username,userPass):
    token = getAuthTokenForUser(username,userPass)
    return keycloak_openid.userinfo(token)


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
