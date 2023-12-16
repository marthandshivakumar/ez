from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UploadFile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    File=models.FileField(upload_to='uploads/')
    File_type=models.CharField(max_length=20)

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    url=models.CharField(max_length=300,null=True,blank=True)
    email=models.BooleanField(default=False)
    is_ops_user=models.BooleanField(default=False)
