from django.db import models
from django.contrib.auth.models import User
from folder.models import Folder
from django.contrib.humanize.templatetags import humanize


class FileManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.objects.get(**kwargs)
        except:
            return None


class File(models.Model):
    file = models.FileField(blank=False, null=False)
    parent = models.ForeignKey(
        Folder, related_name="children_file", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="files")
    shared_among = models.ManyToManyField(
        User, related_name="shared_files")
    privacy = models.BooleanField(default=True)
    trash = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)
    objects = models.Manager()
    custom_objects = FileManager()

    class Meta:
        ordering = ['-last_modified', 'pk']

    def get_created_at(self):
        return humanize.naturaltime(self.created_at)

    def get_last_modified(self):
        return humanize.naturaltime(self.last_modified)
