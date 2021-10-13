# Generated by Django 2.2.2 on 2021-10-01 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotto', '0002_auto_20180507_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='availability',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='kw',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='year',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='edited',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='entry_date',
        ),
        migrations.AddField(
            model_name='ticket',
            name='draw_date',
            field=models.DateField(auto_now=True),
        )
    ]