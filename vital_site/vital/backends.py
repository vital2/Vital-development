from .models import VLAB_User


class EmailAuthBackend(object):

    def authenticate(self, email=None, password=None):
        """
        Authentication method
        """
        try:
            user = VLAB_User.objects.get(email=email)
            if user.check_password(password):
                return user
        except VLAB_User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = VLAB_User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except VLAB_User.DoesNotExist:
            return None
