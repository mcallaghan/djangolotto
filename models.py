from django.db import models
import django.contrib.postgres.fields as dpg

# Create your models here.

class Ticket(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=200)
    kw = models.IntegerField()
    year = models.IntegerField()
    entry_date = models.TimeField(auto_now_add=True)
    edited = models.TimeField(auto_now=True)

    DAYS = (
        ('1','Monday'),
        ('2','Tuesday'),
        ('3','Wednesday'),
        ('4','Thursday'),
        ('5','Friday'),
    )

    availability = dpg.ArrayField(
        models.CharField(choices=DAYS,max_length=1)
    )
