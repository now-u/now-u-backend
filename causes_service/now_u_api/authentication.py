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
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Authentication Failed: Token signature expired')

        # TODO In the future if we support changing email address, we should
        # check if a user with this id already exists (rather than relying on email)
        # If user with that sub exists, create
        # username = payload['sub'] 

        email = payload['email']
        auth_id = payload['sub']

        try:
            user = User.objects.get(email=email)
            if user.auth_id is None:
                user.auth_id = auth_id
                user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(email, auth_id=auth_id)

        return user, key
