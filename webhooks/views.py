from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import json
import asana
import pdb


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
        client = asana.Client.access_token('1/1197770606849972:6ec58af88e7446f312e7b1c9e435baff')
        client.headers["Asana-Enable"] = "string_ids"
        result = client.webhooks.create({
            "target":'https://github-asana-sync.herokuapp.com/asana-webhook', 
            "resource":"1197769418678393"
        })
        print(result)
    

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
        'body': issue.get('body'),
        'author': issue['user']['login'],
        'assignee': issue['assignee']['login'] if issue['assignee'] else '',
        'github_id': task_github_id
    }
    
    asana_task = AsanaTaskManager(type="task", **task_data)

    task_obj = Task.objects.filter(github_id=task_github_id)
    if not task_obj and body['action'] != 'opened':
        Task.objects.create(**task_data)
        asana_task.create()
    #doneget
    if body['action'] == 'opened':
        Task.objects.create(**task_data)
        asana_task.create()

    if comment:
        comment_github_id = comment['id']
        comment_data = {
            'task': Task.objects.get(github_id=task_github_id),
            'body': comment['body'],
            'author': comment['user']['login'],
            'github_id': comment['id']
        }
        asana_comment = AsanaCommentManager(type="comment", **comment_data)
        comment_obj = Comment.objects.filter(github_id=comment_github_id)
        if not comment_obj and body['action'] != 'created':
            Comment.objects.create(**comment_data)
    #done
    if body['action'] == 'created':
        Comment.objects.create(**comment_data)
        asana_comment.create()
    #done
    if body['action'] == 'edited':
        if not body.get('comment'):
            task_obj.update(**task_data)
            asana_task.update()
        else:
            comment_obj.update(**comment_data)
            asana_comment.update()

    if body['action'] == 'assigned':
        task_obj.update(assignee=issue['user']['login'])
        asana_task.assign()

    if body['action'] == 'unassigned':
        task_obj.update(assignee='')
        asana_task.unassign()

    if body['action'] == 'closed':
        task_obj.update(status='DN', is_closed=True)
        asana_task.close()
    #done
    if body['action'] == 'deleted':
        if not body.get('comment'):
            asana_task.delete()
            task_obj.delete()
        else:
            asana_comment.delete()
            comment_obj.delete()
            

    return HttpResponse('pong')


@csrf_exempt
def asana_webhook(request):
    response = HttpResponse(content_type='application/json',)
    print(request.META)
    pdb.set_trace()
    response['X-Hook-Secret'] = request.POST['X-Hook-Secret']
    response.status_code = 200
    return response