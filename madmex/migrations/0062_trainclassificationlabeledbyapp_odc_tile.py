# Generated by Django 2.1.5 on 2020-02-07 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('madmex', '0061_auto_20200207_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainclassificationlabeledbyapp',
            name='odc_tile',
            field=models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='madmex.TrainingSetAndODCTilesForApp'),
        ),
    ]
