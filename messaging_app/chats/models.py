from django.db import models
class user(models.Model):

    first_name = models.CharField(max_length=200, null=False)
    last_name = models.CharField(max_length=200, null=False)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=128)
    phone_number = models.IntegerField(blank=True, null=False,unique=True)

# Create your models here.
