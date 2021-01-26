from django.db import models


class Setting(models.Model):
    """Model representing a user setting for Smart Home"""
    controller_name = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=100)
    value = models.IntegerField()
