# club/models.py
from django.contrib.auth.models import User
from django.db import models

class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='clubs/logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class ClubLeader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    club = models.OneToOneField(Club, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.club.name}"

class ClubMedia(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='clubs/media/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.club.name}"
class ClubEvent(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.club.name}"


# club/models.py (add this class)
class ClubPost(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.club.name}"[:50]

