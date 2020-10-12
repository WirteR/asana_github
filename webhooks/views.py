from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json

from .models import *

# Create your views here.

class Settings(View):
    def get(self, request):
        return HttpResponse('get settings')

    def post(self, request):
        return HttpResponse('post settings')


class DashBoard(View):
    def get(self, request):
        return HttpResponse('Dashboard')


@csrf_exempt
def github_webhook(request):
    if not request.body:
        return HttpResponse(200)

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    Request.objects.create(body=body)

    issue = body['issue']
    comment = body.get('comment')

    task_github_id = issue['id']
    task_data = {
        'title': issue['title'],
        'body': issue.get('body', ''),
        'assignee': issue['user']['login'],
        'github_id': task_github_id
    }
    try:
        task_obj = Task.objects.filter(github_id=task_github_id)
    except:
        Task.objects.create(**task_data)
    print(task_obj)

    if comment:
        comment_github_id = comment['id']
        comment_data = {
            'task': Task.objects.get(github_id=task_github_id),
            'body': comment['body'],
            'author': comment['user']['login'],
            'github_id': comment['id']
        }
        try:
            comment_obj = Comment.objects.filter(github_id=comment_github_id)
        except:
            Comment.objects.create(**comment_data)
        print(comment_obj)

    if body['action'] == 'opened':
        Task.objects.create(**task_data)

    if body['action'] == 'created':
        Comment.objects.create(**comment_data)

    if body['action'] == 'edited':
        if not body.get('comment'):
            task_obj.update(**task_data)

        else:
            comment_obj.update(**comment_data)

    if body['action'] == 'deleted':
        if not body.get('comment'):
            task_obj.delete()

        else:
            comment_obj.delete()

    if body['action'] == 'assigned':
        task_obj.update(assignee=issue['user']['login'])

    if body['action'] == 'unassigned':
        task_obj.update(assignee='')

    return HttpResponse('pong')


@csrf_exempt
@require_POST
def asana_webhook(request):
    return HttpResponse(200)