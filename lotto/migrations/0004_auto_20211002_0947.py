# Generated by Django 2.2.2 on 2021-10-02 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lotto', '0003_auto_20211001_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='email',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='name',
        ),
        migrations.AddField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]