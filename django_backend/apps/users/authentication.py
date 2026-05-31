from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class RevokedTokenJWTAuthentication(JWTAuthentication):
    """Extends JWTAuthentication to honour the User.revoked_since field.

    Any JWT whose `iat` (issued-at) is earlier than the user's revoked_since
    timestamp is rejected, forcing a fresh login after account suspension or
    admin-triggered revocation.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if user.revoked_since is not None:
            iat = validated_token.get('iat')
            if iat and iat < user.revoked_since.timestamp():
                raise InvalidToken('Token has been revoked.')

        return user
