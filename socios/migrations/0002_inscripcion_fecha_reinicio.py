# Generated by Django 4.2.6 on 2023-11-02 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscripcion',
            name='fecha_reinicio',
            field=models.DateField(blank=True, null=True),
        ),
    ]
