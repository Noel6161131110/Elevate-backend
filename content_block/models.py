from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=4)
    email = models.TextField()
    tags = models.TextField()
    user_id = models.TextField(default='')
    
    
class Content(models.Model):
    user_id = models.TextField(default='')
    content = models.TextField()
    audio_location = models.TextField(default='')
    
