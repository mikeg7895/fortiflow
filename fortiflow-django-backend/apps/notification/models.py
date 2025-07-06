from django.db import models
from apps.account.models import CustomUser


class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_global = models.BooleanField(default=False)

    users = models.ManyToManyField(CustomUser, through="NotificationUser", related_name="notifications")

    def __str__(self):
        return self.title


class NotificationUser(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.Notification.title

