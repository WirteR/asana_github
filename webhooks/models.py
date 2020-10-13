from django.db import models

# Create your models here.

STATUSES = [
    ('TD', 'To do'),
    ('DO', 'Doing'),
    ('DN', 'Done'),
]


class Task(models.Model):
    title = models.CharField(max_length=125)
    body = models.TextField(blank=True, default='')
    assignee = models.CharField(max_length=125, blank=True, default='')
    author = models.CharField(max_length=125, default="")
    status = models.CharField(max_length=2, choices=STATUSES, default='TD')
    is_closed = models.BooleanField(default=False)
    github_id = models.IntegerField(null=True, default=None)
    asana_id = models.IntegerField(null=True, default=None)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE) 
    body = models.TextField()
    github_id = models.IntegerField(null=True, default=None)
    asana_id = models.IntegerField(null=True, default=None)
    author = models.CharField(max_length=125, blank=True, default='')

    def __str__(self):
        return self.body


class Request(models.Model):
    body = models.TextField()