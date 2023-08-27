import jwt
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from now_u_api.settings import JWT_SECRET
from users.models import User

class NowuTokenAuthentication(TokenAuthentication): 
    keyword = 'Bearer' # token type

    def authenticate_credentials(self, key):
        try:
            payload = jwt.decode(key, JWT_SECRET, algorithms=["HS256"], audience='authenticated')
        except jwt.DecodeError:
            raise AuthenticationFailed('Authentication Failed: Invalid token')

        # TODO In the future if we support changing email address, we should
        # check if a user with this id already exists (rather than relying on email)
        # If user with that sub exists, create
        # username = payload['sub'] 

        # TODO For now we should store the sub

        email = payload['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # TODO add auth_id to model
            user = User.objects.create_user(email, auth_id=payload['sub'])

        return user, key
