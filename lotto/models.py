from django.db import models
import django.contrib.postgres.fields as dpg
from django.contrib.auth.models import User

# Create your models here.

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    draw_date = models.DateField(null=True)
