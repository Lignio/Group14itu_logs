from keycloak import KeycloakOpenID, keycloak_admin,KeycloakAdmin

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

def getUserInfo(username,userPass):
    token = getAuthTokenForUser(username,userPass)
    return keycloak_openid.userinfo(token)

# Doesn't work yet, need to figure out how this works. 
# Needs a refresh token to log out, which can be gotten like token is got above. Pypi site
# Documents this quite well.
def logoutUser(userAuthToken):
    keycloak_openid.logout(userAuthToken)

# Admin client is used to gain access to a users groups and roles. Is done with user_id, not username.
# Example userID: 47c7a85c-0764-4a20-bbf6-ba7fe2860e26
# UserID is available to see in the keycloak admin console, but is also returned with userinfo sa in
# getAuthTokenForUser
def getUserGroupsAndRoles(userID):
    return admin.get_user_groups(user_id=userID)


def createUser(email, username, password):
    admin.create_user({"email": email,
                                       "username": username,
                                       "enabled": True,
                                       "firstName": "Example",
                                       "lastName": "Example",
                    "credentials": [{"value": "secret","type": password,}]})
