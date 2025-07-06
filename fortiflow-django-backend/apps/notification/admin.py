from django.contrib import admin
from apps.notification.models import Notification, NotificationUser

admin.site.register(Notification)
admin.site.register(NotificationUser)
