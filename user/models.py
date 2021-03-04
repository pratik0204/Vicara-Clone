from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


def filesystem_default_value():
    default_filesystem = {
        "ROOT": {
            "PARENT": None,
            "TYPE": "FOLDER",
            "CHILDREN": {
            }
        }
    }
    return default_filesystem


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    filesystem = models.JSONField(default=filesystem_default_value)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()