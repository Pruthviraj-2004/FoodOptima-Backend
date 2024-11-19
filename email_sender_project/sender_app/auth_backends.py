from django.contrib.auth.backends import BaseBackend
from .models import CompanyManager

class CompanyManagerBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            manager = CompanyManager.objects.get(email=email)
            if manager.check_password(password):
                return manager
        except CompanyManager.DoesNotExist:
            return None

    def get_user(self, manager_id):
        try:
            return CompanyManager.objects.get(pk=manager_id)
        except CompanyManager.DoesNotExist:
            return None
