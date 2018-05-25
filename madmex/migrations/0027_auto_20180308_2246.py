# Generated by Django 2.0 on 2018-03-08 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('madmex', '0026_trainobject_filename'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='model', to='madmex.Model')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheme', models.CharField(default=None, max_length=50)),
                ('key', models.CharField(default=None, max_length=50)),
                ('value', models.CharField(default=None, max_length=150)),
                ('numeric_code', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TrainClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('training_set', models.CharField(default='', max_length=100)),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='madmex.Tag')),
            ],
        ),
        migrations.RemoveField(
            model_name='predicttag',
            name='model',
        ),
        migrations.RemoveField(
            model_name='predictobject',
            name='prediction_tags',
        ),
        migrations.RemoveField(
            model_name='trainobject',
            name='training_tags',
        ),
        migrations.AddField(
            model_name='trainobject',
            name='creation_year',
            field=models.IntegerField(default=2015),
        ),
        migrations.DeleteModel(
            name='PredictTag',
        ),
        migrations.DeleteModel(
            name='TrainTag',
        ),
        migrations.AddField(
            model_name='trainclassification',
            name='train_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='madmex.TrainObject'),
        ),
        migrations.AddField(
            model_name='predictclassification',
            name='predict_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='madmex.PredictObject'),
        ),
        migrations.AddField(
            model_name='predictclassification',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='madmex.Tag'),
        ),
    ]