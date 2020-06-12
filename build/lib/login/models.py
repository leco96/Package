from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserCustom(AbstractUser):
    clave_ciudadano = models.TextField()


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(UserCustom, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")
