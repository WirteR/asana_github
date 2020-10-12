from django.db import models

# Create your models here.

STATUSES = [
    ('TD', 'To do'),
    ('DO', 'Doing'),
    ('DN', 'Done'),
]


class Task(models.Model):
    name = models.CharField(max_length=125)
    description = models.TextField()
    assignee = models.EmailField(max_length=255)
    status = models.CharField(max_length=2, choices=STATUSES, default='TD')
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE) 
    text = models.TextField()