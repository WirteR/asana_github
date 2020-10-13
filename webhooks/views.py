from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json
import asana

from .models import *
from .managers import *
# Create your views here.

class Settings(View):
    def get(self, request):
        return HttpResponse('get settings')

    def post(self, request):
        return HttpResponse('post settings')


class DashBoard(View):
    def get(self, request):
        pass
    #     client = asana.Client.access_token('1/1197770606849972:10e1226268b729592d41e6579a84c9ac')
    #     client.headers["Asana-Enable"] = "string_ids"
    #     result = client.webhooks.create({"target":'https://github-asana-sync.herokuapp.com/asana-webhook', "resource":"1197769418678393"})
    #     print(result)

    # def post(self, request):
    #     secret = request['headers']['X-Hook-Secret']
    #     print('here here')
    #     return {"statusCode":"200",
    #         "headers": {
    #             'Content-Type': 'application/json',
    #             'Accept': 'application/json',
    #             'X-Hook-Secret': secret
    #         }
    #     }


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
        'github_id': task_github_id,
        'resource': 'task'
    }
    try:
        task_obj = Task.objects.filter(github_id=task_github_id)
    except:
        Task.objects.create(**task_data)

    if comment:
        comment_github_id = comment['id']
        comment_data = {
            'task': Task.objects.get(github_id=task_github_id),
            'body': comment['body'],
            'author': comment['user']['login'],
            'github_id': comment['id'],
            'resource': 'comment'
        }
        asana_comment = AsanaManager(type="comment", **comment_data)
        try:
            comment_obj = Comment.objects.filter(github_id=comment_github_id)
        except:
            Comment.objects.create(**comment_data)
        
    asana_task = AsanaManager(type="task", **task_data)

    if body['action'] == 'opened':
        Task.objects.create(**task_data)

    if body['action'] == 'created':
        Comment.objects.create(**comment_data)

    if body['action'] == 'edited':
        if not body.get('comment'):
            task_obj.update(**task_data)
        else:
            comment_obj.update(**comment_data)

    if body['action'] == 'assigned':
        task_obj.update(assignee=issue['user']['login'])

    if body['action'] == 'unassigned':
        task_obj.update(assignee='')

    if body['action'] == 'closed':
        task_obj.update(status='DN', is_closed=True)

    if body['action'] == 'deleted':
        if not body.get('comment'):
            task_obj.delete()
        else:
            comment_obj.delete()

    return HttpResponse('pong')


@csrf_exempt
@require_POST
def asana_webhook(request):
    print('here')
    secret = request['headers']['X-Hook-Secret']
    return {"statusCode":"200",
        "headers": {
             'Content-Type': 'application/json',
             'Accept': 'application/json',
             'X-Hook-Secret': secret
        }
    }