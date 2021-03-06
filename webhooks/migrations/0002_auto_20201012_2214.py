# Generated by Django 2.2 on 2020-10-12 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='body',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='name',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='task',
            name='description',
        ),
        migrations.AddField(
            model_name='comment',
            name='asana_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.CharField(blank=True, default='', max_length=125),
        ),
        migrations.AddField(
            model_name='comment',
            name='github_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='asana_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='body',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='task',
            name='github_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='assignee',
            field=models.CharField(blank=True, default='', max_length=125),
        ),
    ]
