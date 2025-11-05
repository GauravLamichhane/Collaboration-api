from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  
  STATUS_CHOICES = (
    ('online','Online'),#(database_value,human_readable_label)
    ('away','Away'),
    ('busy','Busy'),
    ('offline','Offline'),
  )

  email = models.EmailField(unique=True)
  bio = models.TextField(max_length=500,blank=True)
  avatar = models.ImageField(upload_to='avatars/',null=True,blank=True)
  status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='offline')
  last_seen = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)

  #Making email as primary login field

  USERNAME_FIELD = ['email']
  REQUIRED_FIELDS = ['username']

  class Meta:
    ordering = ['-created_at']
  def __str__(self):
    return self.email
  #this decorator makes full_name act like a field even its a method.
  @property
  def full_name(self):
    return f"{self.first_name}{self.last_name}".strip() or self.username