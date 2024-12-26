from django.db import models

# Create your models here.
class Trend(models.Model):
    _id = models.CharField(max_length=100, primary_key=True)
    trend1 = models.CharField(max_length=255, null=True, blank=True)
    trend2 = models.CharField(max_length=255, null=True, blank=True)
    trend3 = models.CharField(max_length=255, null=True, blank=True)
    trend4 = models.CharField(max_length=255, null=True, blank=True)
    trend5 = models.CharField(max_length=255, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"Trends at {self.datetime}"