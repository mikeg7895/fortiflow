from django.db import models
from apps.account.models import CustomUser
from apps.portfolio.models import Debtor


class Program(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="programs")
    calls_initiated = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    is_paused = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="assignments")
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="assignments")
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE, related_name="assignments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.program.title


class Management(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="managements")
    action = models.CharField(max_length=255)
    type_contact = models.CharField(max_length=255)
    effect = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    phone = models.BigIntegerField()
    date_enagement = models.DateField()
    commitment = models.CharField(max_length=255)
    observation = models.TextField()
    next_management = models.DateField()

    def __str__(self):
        return self.assignment.program.title
