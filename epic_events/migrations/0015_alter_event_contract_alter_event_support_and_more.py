# Generated by Django 5.0.1 on 2024-01-09 05:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epic_events', '0014_alter_event_end_date_alter_event_start_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='contract',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='epic_events.contract'),
        ),
        migrations.AlterField(
            model_name='event',
            name='support',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='location',
            name='street_type',
            field=models.CharField(blank=True, choices=[('', ''), ('rue', 'rue'), ('impasse', 'impasse'), ('avenue', 'avenue'), ('boulevard', 'boulevard'), ('allée', 'allée'), ('chemin', 'chemin')], max_length=100, null=True, verbose_name='Type de voie'),
        ),
    ]
