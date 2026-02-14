from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class PhoneOrEmailBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        if not username or not password:
            return None
        
        try:
            user = User.objects.get(Q(email=username)|Q(phone=username)|Q(username=username))

        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
    