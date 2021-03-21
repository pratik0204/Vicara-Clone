import os
from django.db import models
from django.contrib.auth.models import User

from mysite.storage_backends import PrivateMediaStorage
PRIVACY_CHOICES = (
    ("PRIVATE", "PRIVATE"),
    ("PUBLIC", "PUBLIC"),
)


class File(models.Model):
    # file = models.FileField(blank=False, null=False,
    #                         storage=PrivateMediaStorage())
    file = models.FileField(blank=False, null=False)
    filesystem_id = models.CharField(blank=True, max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="creator", null=True)
    users = models.ManyToManyField(User, blank=True)
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default="PRIVATE",
    )

    def __str__(self):
        return f"{self.filesystem_id} @ {self.timestamp}"

    def get_s3_key(self):
        return os.path.join(self.file.storage.location, self.file.name)
