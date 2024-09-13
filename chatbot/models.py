from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"


# Blog messages
class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    post = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} : {self.post}"
