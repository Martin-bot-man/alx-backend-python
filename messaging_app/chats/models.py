from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(models.Model) :

    first_name = models.CharField(max_length=200, null=False)
    last_name = models.CharField(max_length=200, null=False)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=128, null=False)
    phone_number = models.CharField(max_length=20,blank=True, null=False,unique=True)

    def __str__(self):
       return f"{self.first_name} {self.last_name}"

    

# Create your models here.
class Message(models.Model):
   message_id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False, db_index=True)
   sender= models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_messages')
   message_body = models.TextField()
   conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages',null=True, blank=True )
   sent_at = models.DateTimeField(auto_now_add=True)

class convesation(models.Model):
   conversation_id = models.AutoField(primary_key=True )
   participants = models.ManyToManyField('User', related_name='conversations')
   created_at = models.DateTimeField(auto_now_add=True)  